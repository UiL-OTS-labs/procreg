

from .views import RegistrationCreateView, LandingView, RegistrationsHomeView, \
    RegistrationOverview, RegistrationQuestionEditView, RegistrationDeleteView, \
    RegistrationSummaryView, MinimalDeleteView, MinimalCategoryView, \
    InvolvedManager, StepperView, BlueprintQuestionEditView, ReceiverDeleteView, \
    SoftwareDeleteView
from .lists.listview import MyRegistrationsList, PORegistrationsList




from django.utils import autoreload
from pprint import pprint

reloader = autoreload.get_reloader()

reloader._update_watches()

watched = reloader.watched_files()


print("\nWatched files within Verwerkingsregister:")

pprint(list(p for p in watched if "Verwerkingsregister" in p.as_uri()))

breakpoint()
