from guardian.shortcuts import assign_perm

from sandwich.core.models.form import Form
from sandwich.core.models.role import RoleName


def assign_default_form_permissions(form: Form) -> None:
    """Apply default permissions for a given form instance.

    Since STAFF can't create forms, they only get view_form permissions.
    """
    # apply org-wide role perms
    if form.organization:
        org = form.organization
        owner_role = org.get_role(RoleName.OWNER)
        admin_role = org.get_role(RoleName.ADMIN)
        staff_role = org.get_role(RoleName.STAFF)

        # All org staff can view forms in their org.
        assign_perm("view_form", owner_role.group, form)
        assign_perm("view_form", admin_role.group, form)
        assign_perm("view_form", staff_role.group, form)

        # Only OWNER and ADMIN can change/delete forms.
        assign_perm("change_form", owner_role.group, form)
        assign_perm("change_form", admin_role.group, form)

        assign_perm("delete_form", owner_role.group, form)
        assign_perm("delete_form", admin_role.group, form)
