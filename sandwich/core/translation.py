from modeltranslation.translator import TranslationOptions
from modeltranslation.translator import register

from .models import Template


@register(Template)
class TemplateTranslationOptions(TranslationOptions):
    fields = ("content",)
