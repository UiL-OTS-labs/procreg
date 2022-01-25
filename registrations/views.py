from django.shortcuts import render
from django.views import generic

from .models import Registration
from .forms import NewRegistrationQuestion

# Create your views here.


class RegistrationsHomeView(generic.TemplateView):

    template_name = 'registrations/home.html'


class RegistrationCreateView(generic.CreateView):

    model = Registration
    template_name = 'registrations/new_registration.html'
    form_class = NewRegistrationQuestion
