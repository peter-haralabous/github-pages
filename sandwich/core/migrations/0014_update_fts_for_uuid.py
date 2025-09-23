# Fix FTS5 table to work with UUID primary keys

from django.db import migrations


# Drop the old FTS table and create a new one that works with UUIDs
UPDATE_PATIENT_FTS_FOR_UUID = """
-- Drop old FTS table and triggers
DROP TRIGGER IF EXISTS core_patient_after_update;
DROP TRIGGER IF EXISTS core_patient_after_delete;
DROP TRIGGER IF EXISTS core_patient_after_insert;
DROP TABLE IF EXISTS core_patient_fts;

-- Create new FTS table with UUID support
CREATE VIRTUAL TABLE core_patient_fts USING fts5(
    patient_uuid,
    first_name,
    last_name,
    phn,
    email
);

-- Create triggers that work with UUID primary keys
CREATE TRIGGER core_patient_after_insert
AFTER INSERT ON core_patient
BEGIN
    INSERT INTO core_patient_fts(patient_uuid, first_name, last_name, phn, email)
    VALUES (new.id, new.first_name, new.last_name, new.phn, new.email);
END;

CREATE TRIGGER core_patient_after_delete
AFTER DELETE ON core_patient
BEGIN
    DELETE FROM core_patient_fts WHERE patient_uuid = old.id;
END;

CREATE TRIGGER core_patient_after_update
AFTER UPDATE ON core_patient
BEGIN
    DELETE FROM core_patient_fts WHERE patient_uuid = old.id;
    INSERT INTO core_patient_fts(patient_uuid, first_name, last_name, phn, email)
    VALUES (new.id, new.first_name, new.last_name, new.phn, new.email);
END;

-- Populate FTS table with existing data
INSERT INTO core_patient_fts(patient_uuid, first_name, last_name, phn, email)
SELECT id, first_name, last_name, phn, email FROM core_patient;
"""

# Reverse migration - drop the UUID FTS and restore the old one
RESTORE_OLD_FTS = """
-- Drop UUID FTS table and triggers
DROP TRIGGER IF EXISTS core_patient_after_update;
DROP TRIGGER IF EXISTS core_patient_after_delete;
DROP TRIGGER IF EXISTS core_patient_after_insert;
DROP TABLE IF EXISTS core_patient_fts;

-- Restore old FTS table (this won't work with UUIDs, but needed for reverse migration)
CREATE VIRTUAL TABLE IF NOT EXISTS core_patient_fts USING fts5(
    first_name,
    last_name,
    phn,
    email,
    content='core_patient',
    content_rowid='id'
);
"""


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0013_alter_encounter_id_alter_formiosubmission_id_and_more'),
    ]

    operations = [
        migrations.RunSQL(sql=UPDATE_PATIENT_FTS_FOR_UUID, reverse_sql=RESTORE_OLD_FTS)
    ]
