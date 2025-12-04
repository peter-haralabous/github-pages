import markdown
from django import template

register = template.Library()


@register.filter(name="markdown")
def markdown_filter(text):
    return markdown.markdown(text, extensions=["extra", "sane_lists", "smarty"])
