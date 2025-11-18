{% if patient_full_name %}
- Name: {{ patient_full_name }}
{% endif %}
{% if patient_date_of_birth %}
- Date of Birth: {{ patient_date_of_birth }}
{% endif %}
{% if phn %}
- Provincial Health Card Number: {{ phn }}
{% endif %}
{% if patient_province %}
- Province: {{ patient_province }}
{% endif %}
{% if email %}
- Email: {{ email }}
{% endif %}
