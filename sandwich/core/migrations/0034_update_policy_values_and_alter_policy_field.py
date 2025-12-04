from django.db import migrations
from django.db import models

# Rename old values to new versioned values
POLICY_VALUE_MAP = {
    "THRIVE_TERMS_OF_USE": "THRIVE_TERMS_OF_USE__2020-06-26",
    "THRIVE_PRIVACY_POLICY": "THRIVE_PRIVACY_POLICY__2021-11-09",
    "THRIVE_MARKETING_POLICY": "THRIVE_MARKETING_POLICY__2025-10-16",
}


def forwards(apps, schema_editor):
    Consent = apps.get_model("core", "Consent")
    for old, new in POLICY_VALUE_MAP.items():
        Consent.objects.filter(policy=old).update(policy=new)


def backwards(apps, schema_editor):
    Consent = apps.get_model("core", "Consent")
    for old, new in POLICY_VALUE_MAP.items():
        Consent.objects.filter(policy=new).update(policy=old)


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0033_backfill_user_patient_perms"),
    ]
    operations = [
        migrations.RunPython(forwards, backwards),
        migrations.AlterField(
            model_name="consent",
            name="policy",
            field=models.CharField(
                choices=[
                    ("THRIVE_TERMS_OF_USE__2020-06-26", "Thrive Terms Of Use"),
                    ("THRIVE_PRIVACY_POLICY__2021-11-09", "Thrive Privacy Policy"),
                    ("THRIVE_MARKETING_POLICY__2025-10-16", "Thrive Marketing Policy"),
                ],
                max_length=255,
            ),
        ),
    ]
