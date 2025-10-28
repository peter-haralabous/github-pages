import logging
from typing import TYPE_CHECKING

from guardian.shortcuts import assign_perm

from sandwich.core.models.role import RoleName

if TYPE_CHECKING:
    from sandwich.core.models.patient import Patient

logger = logging.getLogger(__name__)


DEFAULT_ORGANIZATION_ROLE_PERMS = {
    RoleName.OWNER: [
        "assign_task",
        "view_patient",
        "change_patient",
        "create_document",
    ],
    RoleName.ADMIN: [
        "assign_task",
        "view_patient",
        "change_patient",
        "create_document",
    ],
    RoleName.STAFF: [
        "assign_task",
        "view_patient",
        "change_patient",
        "create_document",
    ],
}


def maybe_patient_name(q: str) -> list[str] | None:
    """
    try to turn unstructured text into a patient name

    >>> maybe_patient_name("") is None
    True
    >>> maybe_patient_name("SMITT, CARL")
    ["Carl", "Smitt"]
    >>> maybe_patient_name("SMITT, CARL JOSEPH")
    ["Carl Joseph", "Smitt"]
    >>> maybe_patient_name("sarah wu")
    ["Sarah", "Wu"]
    >>> maybe_patient_name("bowser")
    ["Bowser", ""]
    """
    logger.debug("Parsing patient name from query", extra={"query_length": len(q.strip()), "has_comma": "," in q})

    q = q.strip()
    if len(q) < 3:  # noqa: PLR2004
        logger.debug("Query too short for name parsing", extra={"query_length": len(q)})
        return None

    parts = q.split(",", maxsplit=1)[::-1] if "," in q else q.split(" ", 1)
    result = [p.strip().capitalize() for p in parts]
    if len(result) == 1:
        result.append("")

    logger.debug(
        "Name parsing completed",
        extra={
            "parts_count": len(parts),
            "result_format": "last_first" if "," in q else "first_last",
            "has_last_name": bool(result[1]) if len(result) > 1 else False,
        },
    )

    return result


def assign_default_patient_permissions(patient: "Patient") -> None:
    """
    Assigns the whole organization that the patient is linked to with patient task perms
    """
    # Patient doesn't belong to any organization
    if patient.organization:
        # Apply org-wide role perms
        for role_name, perms in DEFAULT_ORGANIZATION_ROLE_PERMS.items():
            role = patient.organization.get_role(role_name)
            for perm in perms:
                assign_perm(perm, role.group, patient)
        logger.debug(
            "Provider has been given permissions to patient",
            extra={
                "patient_id": patient.id,
                "organization_id": patient.organization.id,
            },
        )

    # Apply user-owner permissions
    if patient.user:
        patient.assign_user_owner_perms(patient.user)
