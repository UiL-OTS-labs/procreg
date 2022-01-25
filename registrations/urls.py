from django.contrib.auth import views as auth_views
from django.urls import path

from .views import RegistrationsHomeView, RegistrationCreateView

app_name = 'registrations'

urlpatterns = [
    path('', RegistrationsHomeView.as_view(), name='home'),
    path('new/', RegistrationCreateView.as_view(), name='new_registration'),
]
