## Immunizations
{% for immunization in immunizations %}
[{{ immunization.name }} ({{ immunization.date|date:"Y-m-d" }})]({{ immunization.get_absolute_url }})
{% empty %}
No immunizations found
{% endfor %}

## Practitioners
{% for practitioner in practitioners %}
[Dr. {{ practitioner.name }}]({{ practitioner.get_absolute_url }})
{% empty %}
No practitioners found
{% endfor %}

## Conditions
{% for condition in conditions %}
[{{ condition.name }}]({{ condition.get_absolute_url }})
{% empty %}
No conditions found
{% endfor %}
