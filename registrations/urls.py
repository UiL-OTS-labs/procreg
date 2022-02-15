from django.contrib.auth import views as auth_views
from django.urls import path

from .views import RegistrationsHomeView, RegistrationCreateView, \
    RegistrationOverview, RegistrationQuestionEditView, RegistrationDeleteView
from .forms import QUESTIONS
from .blueprints import RegistrationBlueprint

app_name = 'registrations'

urlpatterns = [
    path('', RegistrationsHomeView.as_view(), name='home'),
    path('new/', RegistrationCreateView.as_view(), name='new_registration'),
    path('<int:reg_pk>/', RegistrationOverview.as_view(), name='overview'),
    path('delete/<int:reg_pk>/', RegistrationDeleteView.as_view(),
         name='delete'),
    path('<int:reg_pk>/<str:question>/edit/<int:question_pk>/',
         RegistrationQuestionEditView.as_view(
             question_dict=QUESTIONS,
             parent_pk_arg='reg_pk'),
         name='edit_question'),
]
