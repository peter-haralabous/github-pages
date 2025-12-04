import json
import logging

from django import template
from django.core.serializers.json import DjangoJSONEncoder
from django.template.defaultfilters import json_script
from django.utils.html import format_html
from django.utils.safestring import mark_safe

logger = logging.getLogger(__name__)

register = template.Library()

_json_script_escapes = {
    ord(">"): "\\u003E",
    ord("<"): "\\u003C",
    ord("&"): "\\u0026",
}


@register.simple_tag(takes_context=True)
def json_script_safe(context, value, element_id=None):
    """
    CSP-safe version of json_script
    https://docs.djangoproject.com/en/5.2/ref/templates/builtins/#json-script
    """
    if not hasattr(context, "request") or not hasattr(context.request, "csp_nonce"):
        message = (
            "Something went wrong, the context has no request or nonce"
            " when trying to apply json_script_safe template tag"
        )
        logger.error(message)
        return json_script(value, element_id)

    json_str = json.dumps(value, cls=DjangoJSONEncoder).translate(_json_script_escapes)
    if element_id:
        template = '<script id="{}" type="application/json" nonce="{}">{}</script>'
        args = (element_id, context.request.csp_nonce, mark_safe(json_str))  # noqa: S308 # this is for code
    else:
        template = '<script type="application/json" nonce="{}">{}</script>'
        args = (
            context.request.csp_nonce,
            mark_safe(json_str),  # noqa: S308 # this is for code
        )  # type: ignore[assignment]
    return format_html(template, *args)
