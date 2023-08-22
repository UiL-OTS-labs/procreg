from django.template import Template
from django.forms.utils import RenderableMixin
from django.template import loader
from django.core.exceptions import ObjectDoesNotExist

import logging

from registrations.models import Faq, FaqList

logger = logging.getLogger(__name__)

class RenderableFaqList():

    template_name = "registrations/faqlist.html"

    def __init__(self, slug=None, faqs=[]):
        self.faqlist = None
        self.faqs = set()

        # If given a slug, fetch the faqlist for that slug
        if slug:
            try:
                self.faqlist = FaqList.objects.get(
                    slug=slug,
                )
                self.faqs = set(self.faqlist.faqs.all())
            except ObjectDoesNotExist as e:
                logger.warning(
                    f"Non-existent FAQList with slug {slug} was requested",
                    e
                )
        # Add provided faqs to our list
        for faq in faqs:
            if type(faq) == str:
                faq = Faq.objects.get(slug=faq)
            self.faqs.add(faq)

    def render(self, context={}):
        template = loader.get_template(self.template_name)
        context.update(
            {
                "faqs": self.faqs,
            },
        )
        return template.render(context.flatten())
