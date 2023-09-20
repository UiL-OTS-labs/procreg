from django.urls import reverse
from django.template import loader

from cdh.questions import questions

from registrations.progress import ProgressItemMixin
from registrations.models import Registration


class RegistrationQuestionMixin(ProgressItemMixin):

    show_progress = True
    extra_form_kwargs = []
    
    # faqs contains (link, faq_title) pairs for in the
    # help sidebar
    faqs = [] 

    def __init__(self, *args, **kwargs):
        self.blueprint = kwargs.pop("blueprint", None)
        self.registration = kwargs.pop('registration', None)
        self.view_kwargs = kwargs.pop('view_kwargs', None)
        return super().__init__(*args, **kwargs)

    def get_registration(self):
        if not getattr(self, "registration"):
            self.registration = self.blueprint.object
        return self.registration

    def get_blueprint(self):
        return self.blueprint

    def get_edit_url(self):

        reverse_kwargs = {
            'question': self.slug,
            'question_pk': self.instance.pk,
            'reg_pk': self.get_registration().pk,
        }

        if reverse_kwargs["question_pk"] is None:
            reverse_kwargs.pop("question_pk")

        return reverse(
            'registrations:edit_question',
            kwargs=reverse_kwargs,
        )


class PlaceholderQuestion(RegistrationQuestionMixin, questions.Question):
    title = "Placeholder"
    description = "Description of placeholder question"
    is_editable = True

    class Meta:
        model = Registration
        fields = []

    def __init__(self, slug="placeholder", *args, **kwargs):
        super().__init__(self)
        self.slug = slug
        self.disabled = True

    def get_edit_url(self):
        return False



class TemplatedFormMixin():

    def render(self, context={}):
        """This is kind of silly, but I want to implement custom form
        template  as closely as possible to the django 4 way so the
        upgrade path is easy."""
        if not self.use_custom_template:
            return super().render()
        template = loader.get_template(self.template_name)
        context.update(
            self.get_form_context()
        )
        return template.render(context.flatten())

    def get_form_context(self):
        return {
            "question": self,
            "editing": True,
        }



class QuestionViewArgumentsMixin():
    """Use this mixin to receive arguments from the calling view"""

    view_arguments = []

    def __init__(self, *args, **kwargs):
        for arg_name in self.view_arguments:
            arg_value = kwargs.pop("arg_name", None)
            setattr(self, arg_name, arg_value)
        return super().__init__(*args, **kwargs)

