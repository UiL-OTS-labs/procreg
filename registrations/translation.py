from modeltranslation.translator import register, TranslationOptions
from .models import Faq

@register(Faq)
class FaqTranslationOptions(TranslationOptions):
    fields = ('title', 'answer', "external_url", "external_url_text")
