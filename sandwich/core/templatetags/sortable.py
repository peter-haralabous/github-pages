from django import template
from django.utils.html import format_html

register = template.Library()


@register.simple_tag(takes_context=True)
def sortable_column(context, label, field):
    request = context["request"]
    sort = context.get("sort", "")

    params = request.GET.copy()
    current_sort = sort or ""

    params.pop("sort", None)
    params.pop("page", None)  # reset pagination on sort change

    if current_sort == field:
        new_sort = f"-{field}"
        indicator = " ▲"
    elif current_sort == f"-{field}":
        new_sort = field
        indicator = " ▼"
    else:
        new_sort = field
        indicator = ""

    if new_sort:
        params["sort"] = new_sort

    querystring = params.urlencode()

    return format_html('<a href="?{}">{}{}</a>', querystring, label, indicator)
