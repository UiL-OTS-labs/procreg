from django.shortcuts import render
from django.views import generic
from django.urls import reverse_lazy

from uil.questions.views import BlueprintView, QuestionEditView

from .models import Registration
from .forms import NewRegistrationQuestion
from .blueprints import RegistrationBlueprint


# Create your views here.


class RegistrationsHomeView(generic.ListView):

    model = Registration
    template_name = 'registrations/home.html'

    def get_queryset(self,):

        qs = Registration.objects.all()
        return qs

class RegistrationOverview(BlueprintView):

    blueprint = RegistrationBlueprint
    pk_url_kwarg = "reg_pk"
    template_name = "registrations/overview.html"

    def get_object(self,):

        return self.model.objects.get(
            pk=self.kwargs.get(self.pk_url_kwarg))

class RegistrationQuestionEditView(QuestionEditView,):

    def get_success_url(self):

        return reverse('registrations:overview',
                       kwargs={'reg_pk': self.kwargs.get('reg_pk')}
        )


class RegistrationCreateView(generic.CreateView):

    model = Registration
    template_name = 'registrations/new_registration.html'
    form_class = NewRegistrationQuestion
    success_url = reverse_lazy("registrations:home")

class RegistrationDeleteView(generic.DeleteView):

    model = Registration
    template_name = "registrations/delete_registration.html"
    success_url = reverse_lazy("registrations:home")
    pk_url_kwarg = 'reg_pk'
