## Immunizations
{% for immunization in immunizations %}
[{{ immunization.name }} ({{ immunization.date|date:"Y-m-d" }})]({{ immunization.get_absolute_url }})
{% empty %}
No immunizations found
{% endfor %}

## Practitioners
{% for practitioner in practitioners %}
[{{ practitioner.name }}]({{ practitioner.get_absolute_url }})
{% empty %}
No practitioners found
{% endfor %}

## Conditions
{% for condition in conditions %}
[{{ condition.name }}]({{ condition.get_absolute_url }}) | Status: {{ condition.status }} | Onset: {{ condition.onset|date:"Y-m-d"|default:"Unknown" }}{% if condition.abatement %} | Resolved: {{ condition.abatement|date:"Y-m-d" }}{% endif %}
{% empty %}
No conditions found
{% endfor %}
