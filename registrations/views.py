import logging

from django.shortcuts import render
from django.views import generic
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin

from cdh.questions.views import BlueprintMixin, QuestionView, \
    QuestionDeleteView, QuestionCreateView, QuestionFromURLMixin, \
    QuestionEditView


from .models import Registration, ParticipantCategory, Involved
from .forms import NewRegistrationQuestion, FacultyQuestion, CategoryQuestion
from .blueprints import RegistrationMixin
from .mixins import ProgressItemMixin

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


class RegistrationSummaryView(
        ProgressItemMixin,
        RegistrationMixin,
        BlueprintMixin,
        generic.TemplateView,
):

    template_name = 'registrations/summary.html'
    extra_context = {"stepper": True}
    title = "registrations:views:summary_title"
    description = "registrations:views:summary_description"
    slug = "summary"

    def get_object(self,):
        return self.get_registration()

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['completed'] = self.blueprint.completed

        return context

    def get_edit_url(self,):
        reg_pk = self.reg_pk
        return reverse(
            "registrations:summary",
            kwargs={
                "reg_pk": reg_pk,
            },
        )

class QuestionFromBlueprintMixin(
):
    """Get the question to edit from the blueprint."""

    question_class_kwarg = "question"

    def get_question(self):
        """Use the provided kwarg to get the instatiated question
        from our blueprint."""
        question_kwargs = {
            "slug": self.kwargs.get(self.question_class_kwarg),
        }
        if "question_pk" in self.kwargs:
            question_pk = self.kwargs.get("question_pk")
            question_kwargs["question_pk"] = question_pk
        blueprint = self.get_blueprint()
        search = blueprint.get_question(
            **question_kwargs,
        )
        if search is None:
            breakpoint()
            raise RuntimeError(
                f"No Question found in blueprint for given args: \
                {question_kwargs}",
            )
        elif type(search) is list:
            raise RuntimeError(
                f"Got multiple possible questions for given slug: \
                {question_kwargs}",
            )
        else:
            return search

    def get_question_object(self):
        return self.get_question().instance

    def get_form(self):
        if self.request.method in ('POST', 'PUT'):
            return super().get_form()
        return self.get_question()

    def get_question_class(self):
        return type(self.get_question())


class BlueprintQuestionEditView(
        QuestionFromBlueprintMixin,
        RegistrationMixin,
        QuestionEditView,
):

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

    def form_invalid(self, form):
        #  breakpoint()
        return super().form_invalid(form)


class RegistrationQuestionEditView(
        QuestionFromURLMixin,
        RegistrationMixin,
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

    def get_form_kwargs(self):
        self.question_data["registration"] = self.get_registration()
        return super().get_form_kwargs()

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


class RegistrationCreateView(generic.CreateView,
                             LoginRequiredMixin):

    "Create a new Registration object using the title question."

    model = Registration
    template_name = 'registrations/new_registration.html'
    form_class = NewRegistrationQuestion
    success_url = reverse_lazy("registrations:home")

    def form_valid(self, form):
        """Set creator of registration."""
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class RegistrationDeleteView(
        generic.DeleteView,
        RegistrationMixin,
):

    "Basic Django delete view for Registrations"

    model = Registration
    template_name = "registrations/delete_registration.html"
    success_url = reverse_lazy("registrations:home")
    pk_url_kwarg = 'reg_pk'


class InvolvedManager(ProgressItemMixin,
                      RegistrationMixin,
                      generic.TemplateView,
                      ):

    title = "registrations:views:involved_manager_title"
    description = "registrations:views:involved_manager_description"
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
        return context

    def get_involved_groups(self):
        return self.blueprint.selected_groups

    def get_edit_url(self):
        reverse_kwargs = {
            "reg_pk": self.registration.pk,
            "group_type": self.group_type,
        }
        return reverse(
            "registrations:involved_manager",
            kwargs=reverse_kwargs,
        )


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


class MinimalCategoryView(generic.TemplateView,
                          RegistrationMixin):

    template_name = "registrations/minimal/categories.html"

    def get_context_data(self, *args, **kwargs):

        context = super().get_context_data(*args, **kwargs)
        registration = self.get_registration()
        cat_qs = ParticipantCategory.objects.filter(
            registration=registration)

        context['categories'] = cat_qs
        return context


class MinimalDeleteView(QuestionDeleteView,
                        RegistrationMixin,
                        ):

    model = ParticipantCategory
    template_name = "registrations/minimal/delete.html"
    success_url = reverse_lazy('main:empty')

    def get_context_data(self, *args, **kwargs):

        context = super().get_context_data(*args, **kwargs)
