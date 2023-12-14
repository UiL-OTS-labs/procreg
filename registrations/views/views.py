import logging

from django.shortcuts import render
from django.views import generic
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.translation import gettext_lazy as _

from cdh.questions.views import BlueprintMixin, QuestionView, \
    QuestionDeleteView, QuestionCreateView, QuestionFromURLMixin, \
    QuestionEditView, SingleQuestionMixin

from django import forms

from registrations.models import Registration, ParticipantCategory, Involved, \
    Software, Receiver, Faq, Attachment, Faq
from registrations.questions import NewRegistrationQuestion, FacultyQuestion, \
    CategoryQuestion, PoResponseQuestion, UserResponseQuestion
from registrations.mixins import RegistrationMixin, RegistrationQuestionMixin
from registrations.progress import ProgressItemMixin
from registrations.blueprints import RegistrationBlueprint

debug = logging.debug


class RegistrationsHomeView(LoginRequiredMixin,
                            generic.ListView,
                            ):

    "Lists a user's available registrations"

    model = Registration
    template_name = 'registrations/home.html'

    def get_queryset(self,):
        qs = Registration.objects.all()
        return qs

class LandingView(
        generic.TemplateView,
):
    template_name = "registrations/landing.html"

    def get_faqs(self,):
        qs = Faq.objects.filter(
            front_page=True,
        )
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["faqs"] = self.get_faqs()
        return context


class RegistrationOverview(RegistrationMixin,
                           BlueprintMixin,
                           generic.TemplateView
                           ):

    """The main page which shows basic Registration info as editable
    questions and progress."""

    pk_url_kwarg = "reg_pk"
    template_name = "registrations/overview.html"

    def get_object(self,):
        return self.get_registration()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        top_questions = self.blueprint.top_questions
        context['top_questions'] = top_questions
        return context

class BlueprintQuestionEditView(
        RegistrationQuestionMixin,
        QuestionEditView,
):

    def get_success_url(self):
        # Rebuild blueprint before getting desired next
        # The answer might change if new info was POSTed
        self.blueprint = None
        self.blueprint = self.get_blueprint()
        if hasattr(self.get_question(), 'get_success_url'):
            return self.get_question().get_success_url()
        bp_next = self.blueprint.get_desired_next_url()
        if bp_next:
            return bp_next
        return reverse_lazy(
            'registrations:overview',
            kwargs={
                'reg_pk': self.kwargs.get('reg_pk')
            }
        )

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["stepper"] = self.get_question_class().show_progress
        return context

    def get_template_names(self):
        "Insert the preferred procreg templates for questions"
        template_names = super().get_template_names()
        template_names.insert(0, "registrations/question.html")
        if self.get_question_class().show_progress:
            template_names.insert(0, "registrations/question_progress.html")
        return template_names

    def form_invalid(self, form):
        #  breakpoint()
        return super().form_invalid(form)


class RegistrationQuestionEditView(
        QuestionFromURLMixin,
        RegistrationQuestionMixin,
        QuestionEditView,
):

    "Edit a question relating to a Registration or a submodel"

    # These kwargs get sent on to the Question class, if available
    extra_form_kwargs = [
    ]

    def get_success_url(self):
        if hasattr(self.get_question(), 'get_success_url'):
            return self.question.get_success_url()
        # Rebuild blueprint before getting desired next
        # The answer might change if new info was POSTed
        self.blueprint = None
        self.blueprint = self.get_blueprint()
        bp_next = self.blueprint.get_desired_next_url()
        if bp_next:
            return bp_next
        return reverse_lazy(
            'registrations:overview',
            kwargs={
                'reg_pk': self.kwargs.get('reg_pk')
            }
        )

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["stepper"] = self.get_question_class().show_progress
        return context

    def get_template_names(self):
        "Insert the preferred procreg templates for questions"
        template_names = super().get_template_names()
        template_names.insert(0, "registrations/question.html")
        if self.get_question_class().show_progress:
            template_names.insert(0, "registrations/question_progress.html")
        return template_names

    def form_invalid(self):
        #  breakpoint()
        return super().form_invalid()
    
class RegistrationSummaryView(
        ProgressItemMixin,
        RegistrationMixin,
        BlueprintMixin,
        QuestionEditView,
):

    template_name = 'registrations/summary.html'
    extra_context = {"stepper": True}
    title = _("registrations:views:summary_title")
    description = _("registrations:views:summary_description")
    slug = "summary"
    question_class = UserResponseQuestion
    model = Registration
    pk_url_kwarg = 'reg_pk'

    def get_object(self,):
        return self.get_registration()

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['completed'] = self.blueprint.completed
        context['responses'] = self.blueprint.responses

        return context
    
    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super().get_form_kwargs(*args, **kwargs)
        user = self.request.user
        kwargs.update({"user": user})
        return kwargs

    def get_edit_url(self,):
        reg_pk = self.reg_pk
        return reverse(
            "registrations:summary",
            kwargs={
                "reg_pk": reg_pk,
            },
        )

    def get_success_url(self,):
        success_url = reverse(
            "registrations:summary",
            kwargs={
                "reg_pk": self.get_registration().pk,
            }
        )
        return success_url

class RegistrationResponseView(
    RegistrationMixin,
    QuestionEditView,
):
    template_name = "registrations/response.html"
    model = Registration
    question_class = PoResponseQuestion
    pk_url_kwarg = 'reg_pk'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        blueprint = self.get_blueprint()
        context['completed'] = blueprint.completed
        context['responses'] = blueprint.responses
        return context

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super().get_form_kwargs(*args, **kwargs)
        user = self.request.user
        kwargs.update({"user": user})
        return kwargs

    def get_allowed_users(self):
        user = self.request.user
        allowed = []
        if "PO" in [g.name for g in user.groups.all()]:
            allowed.append(user)
        return allowed

    def get_object(self):
        return self.get_question_object()
    
    def get_success_url(self):
        return reverse(
            "registrations:po_list",
            )

class RegistrationCreateView(
        LoginRequiredMixin,
        generic.CreateView,
):

    "Create a new Registration object using the title question."

    model = Registration
    template_name = 'registrations/new_registration.html'
    form_class = NewRegistrationQuestion
    success_url = reverse_lazy("registrations:home")

    def form_valid(self, form):
        """Set creator of registration."""
        form.instance.created_by = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        registration = self.object
        return reverse(
            "registrations:overview",
            kwargs={"reg_pk": registration.pk},
        )


class RegistrationDeleteView(
        generic.DeleteView,
        RegistrationQuestionMixin,
):

    "Basic Django delete view for Registrations"

    model = Registration
    template_name = "registrations/delete_registration.html"
    success_url = reverse_lazy("registrations:home")
    pk_url_kwarg = 'reg_pk'


class InvolvedManager(
        ProgressItemMixin,
        RegistrationQuestionMixin,
        generic.TemplateView,
):

    title = _("registrations:views:involved_manager_title")
    description = _("registrations:views:involved_manager_description")
    template_name = "registrations/involved_manager.html"
    slug = "involved_manager"
    extra_context = {
        "show_progress": True,
        "stepper": True,
    }

    def __init__(self, *args, **kwargs):
        self.registration = kwargs.get("registration")
        self.group_type = kwargs.get("group_type")
        return super().__init__(*args, **kwargs)

    def get_queryset(self):
        qs = Involved.objects.filter(
            registration=self.registration,
            group_type=self.kwargs["group_type"],
        )
        return qs

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["groups"] = self.get_involved_groups()
        context["questions"] = self.collect_questions()
        return context

    def collect_questions(self):
        questions = {
            group_type: {
                "existing": [],
            } for group_type in self.get_involved_groups()
        }
        for question in self.blueprint.questions:
            if question.slug == "new_involved":
                if question.instance.pk is not None:
                    questions[question.instance.group_type]["existing"] += [question]
                else:
                    questions[question.instance.group_type]["new"] = question
        return questions

    def get_involved_groups(self):
        return self.blueprint.selected_groups

    def get_edit_url(self):
        reverse_kwargs = {
            "reg_pk": self.registration.pk,
        }
        return reverse(
            "registrations:involved_manager",
            kwargs=reverse_kwargs,
        )


class DocumentsManager(
        ProgressItemMixin,
        RegistrationQuestionMixin,
        generic.TemplateView,
):
    pass


class ReceiverDeleteView(
        generic.DeleteView,
        BlueprintMixin,
):

    blueprint_class = RegistrationBlueprint
    blueprint_pk_kwarg = "reg_pk"
    template_name = "registrations/crud/delete_receiver.html"
    pk_url_kwarg = "receiver_pk"
    model = Receiver

    def get_success_url(self):
        return reverse(
            "registrations:edit_question",
            kwargs={
                "reg_pk": self.get_blueprint().object.pk,
                "question": "receivers",
                "question_pk": self.get_blueprint().object.pk,
            })

class SoftwareDeleteView(
        generic.DeleteView,
        BlueprintMixin,
):

    template_name = "registrations/crud/delete_software.html"
    blueprint_class = RegistrationBlueprint
    blueprint_pk_kwarg = "reg_pk"
    pk_url_kwarg = "software_pk"
    model = Software

    def get_success_url(self):
        return reverse(
            "registrations:edit_question",
            kwargs={
                "reg_pk": self.get_blueprint().object.pk,
                "question": "software",
                "question_pk": self.get_blueprint().object.pk,
            })


class AttachmentDeleteView(
        generic.DeleteView,
        BlueprintMixin,
):

    template_name = "registrations/crud/delete_software.html"
    blueprint_class = RegistrationBlueprint
    blueprint_pk_kwarg = "reg_pk"
    pk_url_kwarg = "attachment_pk"
    model = Attachment

    def get_success_url(self):
        return reverse(
            "registrations:edit_question",
            kwargs={
                "reg_pk": self.get_blueprint().object.pk,
                "question": "attachments",
                "question_pk": self.get_blueprint().object.pk,
            })


class StepperView(RegistrationQuestionEditView):
    template_name = "registrations/stepper_view.html"

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["stepper"] = True
        slug = self.kwargs.get("slug", "no_slug_provided")
        context["slug"] = slug
        return context

    def get_template_names(self):
        return [self.template_name]


class FaqDetailView(
        generic.DetailView,
        ):

    template_name = "registrations/display_faq.html"
    model = Faq
    context_object_name = "faq"
