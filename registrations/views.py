import logging

from django.shortcuts import render
from django.views import generic
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import LoginRequiredMixin

from cdh.questions.views import BlueprintView, QuestionEditView, \
    QuestionDeleteView, QuestionCreateView

from .models import Registration, ParticipantCategory, Involved
from .forms import NewRegistrationQuestion, FacultyQuestion, CategoryQuestion
from .blueprints import RegistrationBlueprint
from .mixins import RegistrationMixin

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
                           BlueprintView):

    """The main page which shows basic Registration info as editable
    questions and progress."""

    pk_url_kwarg = "reg_pk"
    template_name = "registrations/overview.html"

    def get_object(self,):
        self.get_blueprint()
        return self.get_registration()

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        top_questions = [
            NewRegistrationQuestion,
            FacultyQuestion,
        ]

        context['top_questions'] = [
            self.blueprint.instantiate_question(q) for q in top_questions
        ]

        categories = ParticipantCategory.objects.filter(
            registration=self.object)
        context['categories'] = [CategoryQuestion(instance=cat) for cat in categories]

        return context

class RegistrationSummaryView(RegistrationMixin,
                              BlueprintView):

    template_name = 'registrations/summary.html'
    extra_context = {"show_progress": True}

    def get_object(self,):

        return self.get_registration()

    def get_context_data(self, *args, **kwargs):

        context = super().get_context_data(**kwargs)

        context['completed'] = self.blueprint.instantiate_completed()

        return context
    

class RegistrationQuestionEditView(QuestionEditView,
                                   RegistrationMixin,
                                   BlueprintView,
                                   ):

    "Edit a question relating to a Registration or a submodel"

    def get_success_url(self):
        self.question = self.get_form()
        if hasattr(self.question, 'get_success_url'):
            return self.question.get_success_url()
        # Rebuild blueprint before getting desired next
        # The answer might change if new info was POSTed
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

        "Send the parent reg_pk to the Question's __init__()"

        kwargs = super().get_form_kwargs()
        reg_pk = self.kwargs.get('reg_pk')
        kwargs.update({'reg_pk': reg_pk})
        kwargs.update({'registration': self.get_registration()})
        return kwargs

    def get_context_data(self, *args, **kwargs):

        context = super().get_context_data(*args, **kwargs)

        context["question"] = self.question
        context["show_progress"] = True

        return context

    def get_template_names(self):

        "Insert the preferred procreg templates for questions"

        template_names = super().get_template_names()

        template_names.insert(0, "registrations/question.html")

        if self.question.show_progress:
            template_names.insert(0, "registrations/question_progress.html")
        return template_names


class RegistrationCreateView(generic.CreateView,
                             LoginRequiredMixin):

    "Create a new Registration object using the title question."

    model = Registration
    template_name = 'registrations/new_registration.html'
    form_class = NewRegistrationQuestion
    success_url = reverse_lazy("registrations:home")

class RegistrationDeleteView(generic.DeleteView,
                             RegistrationMixin):

    "Basic Django delete view for Registrations"

    model = Registration
    template_name = "registrations/delete_registration.html"
    success_url = reverse_lazy("registrations:home")
    pk_url_kwarg = 'reg_pk'


class InvolvedManager(generic.TemplateView,
                      RegistrationMixin,
                      BlueprintView,
                      ):

    title = "registrations:views:involved_manager_title"
    description = "registrations:views:involved_manager_description"
    template_name = "registrations/involved_manager.html"
    slug = "manager"
    extra_context = {
        "show_progress": True,
    }

    def __init__(self, *args, **kwargs):

        self.registration = kwargs.get("registration")
        self.group_type = kwargs.get("group_type")

        if not self.group_type:
            self.group_type = "consent"
        else:
            self.slug = self.group_type + "_manager"

        self.object = None

        return super().__init__(*args, **kwargs)

    def get_queryset(self):

        return Involved.objects.filter(
            registration=self.registration,
            group_type=self.group_type,
        )

    def get_context_data(self, *args, **kwargs):

        context = super().get_context_data(*args, **kwargs)
        context[object] = self.get_object()
        return context

    def get_object(self):
        return self.registration

    def get_edit_url(self):

        reverse_kwargs = {
            "reg_pk": self.registration.pk,
            "group_type": self.group_type,
        }
        return reverse(
            "registrations:involved_manager",
            kwargs=reverse_kwargs,
        )


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
