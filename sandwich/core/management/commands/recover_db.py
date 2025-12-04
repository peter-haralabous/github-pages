import time

import boto3
from botocore.exceptions import ClientError
from django.core.management.base import BaseCommand
from django.core.management.base import CommandError

from sandwich.core.management.lib.input import InputMixin
from sandwich.core.management.lib.logging import LoggingMixin
from sandwich.core.management.lib.report import ReportMixin
from sandwich.core.management.lib.subcommand import SubcommandMixin


class Command(InputMixin, LoggingMixin, SubcommandMixin, ReportMixin, BaseCommand):
    help = """
    Recover the database from a backup. There are 3 steps to this command.

    1. Locate the backup you want to recover from
       `uv run manage.py recover_db list --resource-type rds`
       Note the 'ResourceArn' of the snapshot
    2. Make a new database from that snapshot:
       ```
       uv run manage.py recover_db restore \
       --recovery-point-arn=<snapshot from step 1> \
       --resource-type=rds \
       --new-name=integration-sandwich-restored-2025-01-01 \
       --original-name=integration-sandwich-sandwich \
       --monitor
       ```
    3. Update terraform to use the new database.
       a) in Terraform, locate the aws_db_instance (or s3) and update the identifier to the new-name you set in step 2
       b) Run `./bin/terraform.sh <stack> state rm aws_db_instance.<original-name>`
       c) Run `./bin/terraform.sh <stack> import aws_db_instance.<original-name> <identifier_of_the_newly_created_db>
       d) Run `./bin/terraform.sh <stack> terraform apply`
    """
    noun = "database"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.backup_client = boto3.client("backup", region_name="ca-central-1")
        self.rds_client = boto3.client("rds", region_name="ca-central-1")
        self.backup_vault_name = "integration-source-vault"
        self.iam_role_arn = "arn:aws:iam::153784117502:role/integration-aws-backup-role"

    def add_arguments(self, parser):
        super().add_arguments(parser)

        list_parser = self.add_subcommand(
            "list",
            self.list_recovery_points,
            arguments=[
                (
                    ("--resource-type",),
                    {
                        "choices": ["rds", "s3"],
                        "required": True,
                        "help": "Type of resource to list recovery points for",
                    },
                )
            ],
            help="List recovery points",
        )
        self.add_report_arguments(list_parser)  # type: ignore[misc]

        self.add_subcommand(
            "restore",
            self.restore_recovery_point,
            arguments=[
                (("--recovery-point-arn",), {"required": True, "help": "ARN of the recovery point to restore"}),
                (
                    ("--resource-type",),
                    {"choices": ["rds", "s3"], "required": True, "help": "Type of resource to restore"},
                ),
                (("--new-name",), {"required": True, "help": "New name for the restored resource"}),
                (("--original-name",), {"help": "Original name of the resource (for RDS)"}),
                (("--monitor",), {"action": "store_true", "help": "Monitor the restore job until completion"}),
            ],
            help="Restore a recovery point",
        )

    def handle(self, *args, **options):
        self.verbosity = LoggingMixin.INFO
        self.info("Welcome to the AWS Backup Recovery Command Centre")
        super().handle(*args, **options)

    def list_recovery_points(self, *args, **options):
        resource_type = options["resource_type"]
        self.info(f"Listing recovery points for {resource_type}...")

        try:
            paginator = self.backup_client.get_paginator("list_recovery_points_by_backup_vault")
            pages = paginator.paginate(
                BackupVaultName=self.backup_vault_name,
                ByResourceType="RDS" if resource_type == "rds" else "S3",
            )

            headers = ["RecoveryPointArn", "ResourceArn", "CreationDate", "Status"]
            data = []
            for page in pages:
                for rp in page["RecoveryPoints"]:
                    # Boto doesn't provide LIKE filtering, so we've gotta do it.
                    if "sandwich" not in rp.get("ResourceArn"):
                        continue

                    data.append(
                        [
                            rp.get("RecoveryPointArn"),
                            rp.get("ResourceArn"),
                            rp.get("CreationDate"),
                            rp.get("Status"),
                        ]
                    )

            self.report(headers, data, **options)  # type: ignore[misc]

        except ClientError as e:
            msg = f"Error listing recovery points: {e}"
            raise CommandError(msg) from e

    def restore_recovery_point(self, *args, **options):
        resource_type = options["resource_type"]
        self.info(f"Restoring {resource_type} from {options['recovery_point_arn']}...")

        if resource_type == "rds":
            job_id = self._restore_rds(**options)
        elif resource_type == "s3":
            job_id = self._restore_s3(**options)
        else:
            msg = f"Unsupported resource type: {resource_type}"
            raise CommandError(msg)

        if job_id and options["monitor"]:
            self._monitor_restore_job(job_id)

    def _restore_rds(self, **options):
        recovery_point_arn = options["recovery_point_arn"]
        new_name = options["new_name"]
        original_name = options.get("original_name")

        if not original_name:
            msg = "--original-name is required for RDS restores"
            raise CommandError(msg)

        self.info(f"Getting original configuration for RDS instance: {original_name}")
        try:
            instance = self.rds_client.describe_db_instances(DBInstanceIdentifier=original_name)["DBInstances"][0]
        except ClientError as e:
            msg = f"Error getting original RDS config: {e}"
            raise CommandError(msg) from e

        metadata = {
            "DBInstanceIdentifier": new_name,
            "DBInstanceClass": instance["DBInstanceClass"],
            # I cannot get the db to recreate in the VpcSecurityGroup, the API reports "Bad metadata"
            # with this line in.
            # "VpcSecurityGroupIds": ",".join([sg["VpcSecurityGroupId"] for sg in instance["VpcSecurityGroups"]]),
            "DBSubnetGroupName": instance["DBSubnetGroup"]["DBSubnetGroupName"],
            "Engine": instance["Engine"],
        }

        self.info(f"Starting RDS restore job for {new_name}")
        try:
            response = self.backup_client.start_restore_job(
                RecoveryPointArn=recovery_point_arn,
                Metadata=metadata,
                IamRoleArn=self.iam_role_arn,
                ResourceType="RDS",
            )
            job_id = response["RestoreJobId"]
        except ClientError as e:
            msg = f"Error starting RDS restore job: {e}"
            raise CommandError(msg) from e

        self.info(f"Restore job started with ID: {job_id}")
        return job_id

    def _restore_s3(self, **options):
        recovery_point_arn = options["recovery_point_arn"]
        new_name = options["new_name"]

        metadata = {
            "NewBucketName": new_name,
        }

        self.info(f"Starting S3 restore job for {new_name}")
        try:
            response = self.backup_client.start_restore_job(
                RecoveryPointArn=recovery_point_arn,
                Metadata=metadata,
                IamRoleArn=self.iam_role_arn,
                ResourceType="S3",
            )
            job_id = response["RestoreJobId"]
        except ClientError as e:
            msg = f"Error starting S3 restore job: {e}"
            raise CommandError(msg) from e
        else:
            self.info(f"S3 job started with ID: {job_id}")
            return job_id

    def _monitor_restore_job(self, job_id):
        self.info(f"Monitoring restore job: {job_id}")
        while True:
            try:
                job = self.backup_client.describe_restore_job(RestoreJobId=job_id)
                status = job["Status"]
                self.info(f"Restore job status: {status}")

                if status in ["COMPLETED", "FAILED"]:
                    if status == "COMPLETED":
                        self.info("Restore job completed successfully!")
                    else:
                        self.error(f"Restore job failed: {job.get('StatusMessage', 'No message')}")
                    break

                time.sleep(30)

            except ClientError as e:
                msg = f"Error monitoring restore job: {e}"
                raise CommandError(msg) from e
