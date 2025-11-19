from typing import TYPE_CHECKING

from guardian.shortcuts import assign_perm

from sandwich.core.models.role import RoleName

if TYPE_CHECKING:
    from sandwich.core.models.summary_template import SummaryTemplate


def assign_default_summarytemplate_permissions(summary_template: "SummaryTemplate") -> None:
    """Apply default permissions for a given summary template instance."""
    org = summary_template.organization
    owner_role = org.get_role(RoleName.OWNER)
    admin_role = org.get_role(RoleName.ADMIN)
    staff_role = org.get_role(RoleName.STAFF)

    # All org employee roles can view summary templates in their org.
    assign_perm("view_summarytemplate", owner_role.group, summary_template)
    assign_perm("view_summarytemplate", admin_role.group, summary_template)
    assign_perm("view_summarytemplate", staff_role.group, summary_template)

    # Only OWNER and ADMIN can change/delete summary templates.
    assign_perm("change_summarytemplate", owner_role.group, summary_template)
    assign_perm("change_summarytemplate", admin_role.group, summary_template)

    assign_perm("delete_summarytemplate", owner_role.group, summary_template)
    assign_perm("delete_summarytemplate", admin_role.group, summary_template)
