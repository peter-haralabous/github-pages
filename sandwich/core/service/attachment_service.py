from guardian.shortcuts import assign_perm

from sandwich.core.models.attachment import Attachment
from sandwich.core.models.encounter import Encounter
from sandwich.core.models.role import RoleName

DEFAULT_ORGANIZATION_ROLE_PERMS = {
    RoleName.OWNER: ["view_attachment"],
    RoleName.ADMIN: ["view_attachment"],
    RoleName.STAFF: ["view_attachment"],
}


def assign_default_attachment_permissions(attachment: Attachment) -> None:
    # user perms
    if attachment.uploaded_by:
        assign_perm("view_attachment", attachment.uploaded_by, attachment)
        assign_perm("delete_attachment", attachment.uploaded_by, attachment)
        assign_perm("change_attachment", attachment.uploaded_by, attachment)

    # group perms
    encounters = Encounter.objects.filter(patient__user=attachment.uploaded_by)
    for encounter in encounters:
        for role_name, perms in DEFAULT_ORGANIZATION_ROLE_PERMS.items():
            role = encounter.organization.get_role(role_name)
            for perm in perms:
                assign_perm(perm, role.group, attachment)
