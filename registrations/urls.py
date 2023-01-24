from django.urls import path

from .views import RegistrationsHomeView, RegistrationCreateView, \
    RegistrationOverview, RegistrationQuestionEditView, RegistrationDeleteView, \
    MinimalCategoryView, MinimalDeleteView, RegistrationSummaryView, \
    InvolvedManager, StepperView, BlueprintQuestionEditView
from .forms import QUESTIONS
from .blueprints import RegistrationBlueprint
from .models import ParticipantCategory

app_name = 'registrations'

urlpatterns = [
    path('', RegistrationsHomeView.as_view(), name='home'),
    path('new/', RegistrationCreateView.as_view(), name='new_registration'),
    path('<int:reg_pk>/', RegistrationOverview.as_view(), name='overview'),
    path('delete/<int:reg_pk>/', RegistrationDeleteView.as_view(),
         name='delete'),
    path('<int:reg_pk>/manager/',
         InvolvedManager.as_view(),
         name='involved_manager',
         ),
    # Take heed, the pathspecs below are quite greedy
    path('<int:reg_pk>/<str:question>/edit/<int:question_pk>/',
         RegistrationQuestionEditView.as_view(
             question_dict=QUESTIONS,
             parent_pk_arg='reg_pk'),
         name='edit_question'),
    path('<int:reg_pk>/<str:question>/edit2/<int:question_pk>/',
         BlueprintQuestionEditView.as_view(
             parent_pk_arg='reg_pk'),
         name='edit_question'),
    path('<int:reg_pk>/<str:question>/<str:group_type>/',
         RegistrationQuestionEditView.as_view(
             question_dict=QUESTIONS,
             parent_pk_arg='reg_pk'),
         name='edit_question'),
    path('<int:reg_pk>/<str:question>/create/',
         RegistrationQuestionEditView.as_view(
             question_dict=QUESTIONS,
             parent_pk_arg='reg_pk'),
         name='create_question'),
    path('<int:reg_pk>/summary/',
         RegistrationSummaryView.as_view(),
         name='summary',
         ),
    path('<int:reg_pk>/<str:question>/stepper/<int:question_pk>/',
         StepperView.as_view(
             question_dict=QUESTIONS,
             parent_pk_arg='reg_pk'),
         name='stepper',
         ),
    path('delete/category/<int:pk>/',
         MinimalDeleteView.as_view(
             model=ParticipantCategory),
         # parent_pk_arg='reg_pk',
         name='minimal_delete'
         )
]
