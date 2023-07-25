from django.template import Template
from django.forms.utils import RenderableMixin

from registrations.models import Faq

class FAQList:

    template_name = "registrations/faqs.html"

    def __init__(self, question_slug=None, order=[]):

        self.faqs = []

        for faq in self.from_order(order):
            self.faqs.append(faq)

        if question_slug is not None:
            for faq in self.from_question_slug(question_slug):
                if faq.pk not in self.faqs:
                    self.faqs.append(faq)

    def from_order(self, order):
        """
        Ingest a (mixed) list of FAQ PKs or slugs and yield FAQ
        objects back
        """
        for x in order:
            faq = None
            if type(x) is Int:
                try:
                    faq = Faq.objects.get(pk=x)
                except Exception as e:
                    breakpoint()
            elif type(x) is str:
                try:
                    faq = Faq.objects.get(slug=x)
                except Exception as e:
                    breakpoint()
            if faq is not None:
                yield faq

    def from_question_slug(self, slug):
        return Faq.objects.filter(
            question_slugs__icontains="slug",
        )

    def get_context(self):
        return {
            "faqs": self.faqs,
        }
