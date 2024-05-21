

from .views import RegistrationCreateView, LandingView, RegistrationsHomeView, \
    RegistrationOverview, RegistrationQuestionEditView, RegistrationDeleteView, \
    RegistrationSummaryView, RegistrationResponseView, \
    InvolvedManager, StepperView, BlueprintQuestionEditView, ReceiverDeleteView, \
    SoftwareDeleteView, AttachmentDeleteView, FaqDetailView
from .lists.listview import MyRegistrationsList, PORegistrationsList


from django.utils.autoreload import (
    autoreload_started, file_changed, is_django_path,
)

from django.dispatch import receiver
import os
directory = os.path.join(os.getcwd(), "registrations", "views")

# To have Django's autoreload function correctly when template files
# and python code are intermixed, we need to trigger the reload manually

# Otherwise, the template loader intercepts the file_changed signal
# and only reloads itself if the path is in a template directory.

@receiver(file_changed, dispatch_uid="force_template_reloading",)
def reload_in_template_dir(sender, **kwargs):
    file_path = kwargs.get("file_path")
    print("signal received!")
    if directory in file_path.as_uri():
        print("manually reloading...")
        from django.utils.autoreload import trigger_reload
        trigger_reload(file_path)
    else:
        print("cwd not in path")
    return False


