from django import template
from django.utils.html import format_html

from sandwich.core.models.custom_attribute import CustomAttribute
from sandwich.core.models.custom_attribute import CustomAttributeEnum
from sandwich.core.service.custom_attribute_query import _parse_custom_attribute_id

register = template.Library()


@register.simple_tag()
def attribute_chip(attribute_name, label):
    attr_id = _parse_custom_attribute_id(attribute_name.replace("attr_", "").replace("_", "-"))
    if attr_id:
        attribute = CustomAttribute.objects.get(id=attr_id)
        attr_enum = CustomAttributeEnum.objects.filter(attribute=attribute, label=label).first()
        if attr_enum:
            color_tag = attr_enum.color_code

            if color_tag:
                return format_html(
                    """
                    <div class="tooltip" data-tip="{}">
                        <div style="background-color: #{};" class="badge w-fit">
                            <div style="mix-blend-mode: color-burn;"
                                class="m-2 text-sm text-center min-w-10 max-w-18 truncate">{}
                            </div>
                        </div>
                    </div>""",
                    label,
                    color_tag,
                    label,
                )

    return format_html(
        """
        <div class="tooltip" data-tip="{}">
            <div class="w-fit">
                <div class="m-2 text-sm text-center min-w-10 max-w-18 truncate">{}</div>
            </div>
        </div>
        """,
        label,
        label,
    )
