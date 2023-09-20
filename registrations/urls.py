from django.urls import path

from .views import RegistrationsHomeView, RegistrationCreateView, \
    RegistrationOverview, RegistrationQuestionEditView, RegistrationDeleteView, \
    MinimalCategoryView, MinimalDeleteView, RegistrationSummaryView, \
    InvolvedManager, StepperView, BlueprintQuestionEditView, \
    ReceiverDeleteView, SoftwareDeleteView, LandingView, MyRegistrationsList, \
    PORegistrationsList, AttachmentDeleteView, FaqDetailView
from .questions import QUESTIONS
from .blueprints import RegistrationBlueprint
from .models import ParticipantCategory

app_name = 'registrations'

urlpatterns = [
    path('', MyRegistrationsList.as_view(), name='my_list'),
    path('po_list/', PORegistrationsList.as_view(), name='po_list'),
    path('home/', RegistrationsHomeView.as_view(), name="home"),
    path('landing/', LandingView.as_view(), name='landing'),
    path('<int:reg_pk>/', RegistrationOverview.as_view(), name='overview'),
    path('<int:reg_pk>/manager/',
         InvolvedManager.as_view(),
         name='involved_manager',
         ),

    # Question edit views
    path('<int:reg_pk>/<str:question>/edit/<int:question_pk>/',
         BlueprintQuestionEditView.as_view(
             parent_pk_arg='reg_pk'),
         name='edit_question'),
    path('<int:reg_pk>/<str:question>/create/',
         BlueprintQuestionEditView.as_view(
             parent_pk_arg='reg_pk'),
         name='edit_question'),
    path('<int:reg_pk>/<str:question>/<str:group_type>/',
         BlueprintQuestionEditView.as_view(
             parent_pk_arg='reg_pk'),
         name='edit_question'),
    
    # Misc registration views
    path('<int:reg_pk>/summary/',
         RegistrationSummaryView.as_view(),
         name='summary',
         ),
    path('new/', RegistrationCreateView.as_view(), name='new_registration'),
    
    # Cruddy stuff
    path('delete/<int:reg_pk>/', RegistrationDeleteView.as_view(),
         name='delete'),
    path('delete/category/<int:pk>/',
         MinimalDeleteView.as_view(
             model=ParticipantCategory),
         # parent_pk_arg='reg_pk',
         name='minimal_delete',
         ),
    path("<int:reg_pk>/delete/receiver/<int:receiver_pk>",
         ReceiverDeleteView.as_view(),
         name="delete_receiver",
         ),
    path("<int:reg_pk>/delete/software/<int:software_pk>",
         SoftwareDeleteView.as_view(),
         name="delete_software",
         ),
    path("<int:reg_pk>/delete/attachment/<int:attachment_pk>",
         AttachmentDeleteView.as_view(),
         name="delete_attachment",
         ),

    # Misc
    path("faq/<int:pk>/",
         FaqDetailView.as_view(),
         name="display_faq",
         ),

    # Debug
    path('<int:reg_pk>/<str:question>/stepper/<int:question_pk>/',
         StepperView.as_view(
             question_dict=QUESTIONS,
             parent_pk_arg='reg_pk'),
         name='stepper',
         ),
]
