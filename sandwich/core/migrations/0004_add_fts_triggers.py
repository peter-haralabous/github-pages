from django.db import migrations

CREATE_TRIGGER_SQL = """
CREATE OR REPLACE FUNCTION update_patient_search_vector()
RETURNS TRIGGER AS $$
BEGIN
    NEW.search_vector :=
        setweight(to_tsvector('english', COALESCE(NEW.first_name, '')), 'A') ||
        setweight(to_tsvector('english', COALESCE(NEW.last_name, '')), 'A') ||
        setweight(to_tsvector('english', COALESCE(NEW.phn, '')), 'B') ||
        setweight(to_tsvector('english', COALESCE(NEW.email, '')), 'C');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER patient_search_vector_trigger
    BEFORE INSERT OR UPDATE ON core_patient
    FOR EACH ROW
    EXECUTE FUNCTION update_patient_search_vector();

-- Update existing records
UPDATE core_patient SET search_vector =
    setweight(to_tsvector('english', COALESCE(first_name, '')), 'A') ||
    setweight(to_tsvector('english', COALESCE(last_name, '')), 'A') ||
    setweight(to_tsvector('english', COALESCE(phn, '')), 'B') ||
    setweight(to_tsvector('english', COALESCE(email, '')), 'C');
"""

DROP_TRIGGER_SQL = """
DROP TRIGGER IF EXISTS patient_search_vector_trigger ON core_patient;
DROP FUNCTION IF EXISTS update_patient_search_vector();
"""


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0003_patient_search_vector_and_more"),
    ]

    operations = [migrations.RunSQL(sql=CREATE_TRIGGER_SQL, reverse_sql=DROP_TRIGGER_SQL)]
