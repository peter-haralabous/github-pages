import logging

logger = logging.getLogger(__name__)


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
