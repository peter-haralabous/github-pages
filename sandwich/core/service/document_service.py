from guardian.shortcuts import assign_perm

from sandwich.core.models.document import Document
from sandwich.core.models.role import RoleName


def assign_default_document_permissions(document: Document) -> None:
    # apply org-wide role perms
    if document.patient.organization:
        org = document.patient.organization
        owner_role = org.get_role(RoleName.OWNER)
        admin_role = org.get_role(RoleName.ADMIN)
        staff_roll = org.get_role(RoleName.STAFF)

        # Providers can view and change documents in the org
        assign_perm("view_document", owner_role.group, document)
        assign_perm("view_document", admin_role.group, document)
        assign_perm("view_document", staff_roll.group, document)

        assign_perm("change_document", owner_role.group, document)
        assign_perm("change_document", admin_role.group, document)
        assign_perm("change_document", staff_roll.group, document)

    # apply user-owner permissions
    if document.patient.user:
        user = document.patient.user
        assign_perm("view_document", user, document)
        assign_perm("change_document", user, document)
        assign_perm("delete_document", user, document)
