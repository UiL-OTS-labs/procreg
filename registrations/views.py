from django.shortcuts import render
from django.views import generic
from django.urls import reverse_lazy

from uil.questions.views import BlueprintView, QuestionEditView

from .models import Registration, ParticipantCategory
from .forms import NewRegistrationQuestion, FacultyQuestion, CategoryQuestion
from .blueprints import RegistrationBlueprint





class RegistrationsHomeView(generic.ListView):

    "Lists a user's available registrations"

    model = Registration
    template_name = 'registrations/home.html'

    def get_queryset(self,):

        qs = Registration.objects.all()
        return qs

class RegistrationOverview(BlueprintView):

    "The main page which shows basic Registration info as editable
    questions and progress."

    blueprint = RegistrationBlueprint
    pk_url_kwarg = "reg_pk"
    template_name = "registrations/overview.html"

    def get_object(self,):

        return self.model.objects.get(
            pk=self.kwargs.get(self.pk_url_kwarg))

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        top_questions = [
            NewRegistrationQuestion,
            FacultyQuestion,
        ]

        context['top_questions'] = [
            q(instance=self.object) for q in top_questions
        ]

        categories = ParticipantCategory.objects.filter(
            registration=self.object)

        context['categories'] = [CategoryQuestion(instance=cat) for cat in categories]


        return context

class RegistrationQuestionEditView(QuestionEditView,):

    "Edit a question relating to a Registration or a submodel"

    def get_success_url(self):

        return reverse_lazy('registrations:overview',
                       kwargs={'reg_pk': self.kwargs.get('reg_pk')}
        )

    def get_form_kwargs(self):

        "Send the parent reg_pk to the Question's __init__()"

        kwargs = super().get_form_kwargs()
        reg_pk = self.kwargs.get('reg_pk')
        kwargs.update({'reg_pk': reg_pk})
        return kwargs


class RegistrationCreateView(generic.CreateView):

    "Create a new Registration object using the title question."

    model = Registration
    template_name = 'registrations/new_registration.html'
    form_class = NewRegistrationQuestion
    success_url = reverse_lazy("registrations:home")

class RegistrationDeleteView(generic.DeleteView):

    "Basic Django "

    model = Registration
    template_name = "registrations/delete_registration.html"
    success_url = reverse_lazy("registrations:home")
    pk_url_kwarg = 'reg_pk'
