from django.template import Template
from django.forms.utils import RenderableMixin
from django.template import loader
from django.core.exceptions import ObjectDoesNotExist
from django.utils.html import mark_safe

import logging

from registrations.models import Faq, FaqList

logger = logging.getLogger(__name__)

class RenderableFaqList():

    template_name = "registrations/faqlist.html"

    def __init__(self, slug, faqs=[]):
        # We also accept extra faqs at init time
        self.init_faqs = set(faqs)
        # Retrieve FaqList object
        try:
            self.faqlist = FaqList.objects.get(
                slug=slug,
            )
        except ObjectDoesNotExist as e:
            logger.warning(
                f"Non-existent FAQList with slug {slug} was requested",
            )
            self.faqlist = FaqList.objects.get(
                slug="default",
            )
        # Add general helptext object
        self.help_text = RenderableHelpText(self.faqlist)

    @property
    def faqs(self):
        faqs = set()
        for faq in self.faqlist.faqs.all():
            faqs.add(faq)
        for faq in self.init_faqs:
            if type(faq) == str:
                # This must be a slug, convert it
                # to a FAQ object first
                try:
                    faq = Faq.objects.get(slug=faq)
                except ObjectDoesNotExist as e:
                    logger.warning(
                        f"Non-existent FAQList with slug {faq} was requested",
                        e
                    )
            faqs.add(faq)
        return faqs

    def render(self, context={}):
        template = loader.get_template(self.template_name)
        context.update(
            {
                "faqs": self.faqs,
            },
        )
        return template.render(context.flatten())


class RenderableHelpText():

    def __init__(self, faqlist):
        self.faqlist = faqlist

    def render(self, context):
        return mark_safe(
            f"""<span class="procreg_helptext">"""
            f"{self.faqlist.help_text}"
            f"</span>"
        )
