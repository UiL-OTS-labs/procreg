from django.shortcuts import render
from django.views import generic
from django.urls import reverse_lazy

from .models import Registration
from .forms import NewRegistrationQuestion

# Create your views here.


class RegistrationsHomeView(generic.ListView):

    model = Registration
    template_name = 'registrations/home.html'

    def get_queryset(self,):

        qs = Registration.objects.all()
        return qs




class RegistrationCreateView(generic.CreateView):

    model = Registration
    template_name = 'registrations/new_registration.html'
    form_class = NewRegistrationQuestion
    success_url = reverse_lazy("registrations:home")
