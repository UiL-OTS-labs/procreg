from django.urls import reverse
from django.template import loader, Template

from cdh.questions import questions

from registrations.progress import ProgressItemMixin
from registrations.models import Registration
from registrations.utils import RenderableFaqList


class RegistrationQuestionMixin(ProgressItemMixin):

    show_progress = True
    extra_form_kwargs = []
    
    # The initials faqs variable can be a FAQList slug
    # or other init argument to RenderableFAQList.
    # At runtime self.faqs gets replaced by the
    # RenderableFAQList object.
    faqs = None
    description = Template("")

    def __init__(self, *args, **kwargs):
        # Required arguments for a Registration Question
        self.blueprint = kwargs.pop("blueprint", None)
        self.registration = kwargs.pop('registration', None)
        self.view_kwargs = kwargs.pop('view_kwargs', None)
        # Initialize help text and FAQs
        if not self.faqs:
            # By default, get the FAQList associated with
            # the question slug
            self.faqs = self.slug
        # A RenderableFaqList gathers the FAQ objects
        # and help text to be rendered in the sidebar
        # of this question.
        self.faqs = RenderableFaqList(self.faqs)
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
        from registrations.questions import QUESTIONS
        if self.slug in QUESTIONS.keys():
            # Copy information from uninstantiated question
            source_question = QUESTIONS[self.slug]
            self.title = source_question.title

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

