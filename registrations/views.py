from django.shortcuts import render
from django.views import generic

from .models import Registration
from .forms import NewRegistrationQuestion

# Create your views here.


class RegistrationsHomeView(generic.ListView):

    template_name = 'registrations/home.html'

    def get_queryset(self,):

        return Registration.objects.all()


class RegistrationCreateView(generic.CreateView):

    model = Registration
    template_name = 'registrations/new_registration.html'
    form_class = NewRegistrationQuestion
