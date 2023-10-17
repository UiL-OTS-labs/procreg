from django.template import Template, loader
from django.views.generic.base import ContextMixin
from django.core.exceptions import ImproperlyConfigured

class Renderable(ContextMixin):

    template_name = None

    def get_context(self):
        raise NotImplementedError(
            "Subclasses of Renderable must provide a get_context() method."
        )

    def get_template_name(self):
        if not self.template_name:
            raise ImproperlyConfigured("No template defined")
        return self.template_name

    def render(self, context={}):
        template_name = self.get_template_name()
        template = loader.get_template(template_name)
        context.update(self.get_context_data())
        return template.render(context.flatten())
