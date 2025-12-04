from __future__ import annotations

from typing import Any

from django.db import migrations


def _normalize_patient_id(raw: Any) -> str | None:
    if isinstance(raw, dict):
        val = raw.get("patient_id")
        return str(val) if val else None
    if raw is None:
        return None
    return str(raw)


def backfill_entity_patient(apps, schema_editor):
    Entity = apps.get_model("core", "Entity")
    Patient = apps.get_model("core", "Patient")

    qs = Entity.objects.filter(patient__isnull=True).filter(metadata__has_key="patient_id")

    for ent in qs.iterator():
        raw = (ent.metadata or {}).get("patient_id")
        pid_str = _normalize_patient_id(raw)
        if not pid_str:
            continue

        patient_obj = Patient.objects.filter(pk=pid_str).first()
        if not patient_obj:
            continue

        Entity.objects.filter(pk=ent.pk).update(patient_id=patient_obj.pk)


class Migration(migrations.Migration):
    dependencies = [("core", "0060_entity_patient")]

    operations = [migrations.RunPython(backfill_entity_patient, migrations.RunPython.noop)]
