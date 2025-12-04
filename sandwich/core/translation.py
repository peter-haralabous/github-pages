"""
https://django-modeltranslation.readthedocs.io/en/latest/

 > Registering models and their fields for translation requires the following steps:
 >
 >     Create a translation.py in your app directory.
 >     Create a translation option class for every model to translate.
 >     Register the model and the translation option class at modeltranslation.translator.translator.
 >
 > https://django-modeltranslation.readthedocs.io/en/latest/registration.html

This automatically creates fields like content_en, content_de, etc. based on the LANGUAGES setting.

The translations can be accessed directly but the normal use case "just does the right thing"
by using the get_language() function to get the current language and then access the field dynamically.

Temporarily setting the default language can be done with the override() context manager:

    from django.utils.translation import override
    from sandwich.core.models import Template

    template = Template.objects.first()
    print(template.content)  # prints content in current language
    with override('de'):
        print(template.content)  # prints content in German

"""

from modeltranslation.translator import TranslationOptions
from modeltranslation.translator import register

from .models import Template


@register(Template)
class TemplateTranslationOptions(TranslationOptions):
    fields = ("content",)
