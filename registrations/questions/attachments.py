from cdh.questions import questions
from .helpers import TemplatedFormMixin, RegistrationQuestionMixin
from registrations.models import Registration, Receiver, Attachment
from django.utils.translation import gettext_lazy as _
from django.urls import reverse

class AttachmentsQuestion(
        RegistrationQuestionMixin,
        questions.Question,
        TemplatedFormMixin,
):
    # Django ModelForm compatibility
    class Meta:
        model = Registration
        fields = [
            "third_party_sharing",
        ]
    # Procreg question stuff
    model = Meta.model
    title = _("registrations:forms:receiver_question_title")
    description = _("registrations:forms:receiver_question_description")
    slug = "attachments"
    is_editable = True
    show_progress = True
    # Custom template for Manager inclusion
    template_name = "forms/attachments_form.html"
    use_custom_template = True

    def get_queryset(self):
        """Return the list of receivers currently connected to
        this registration."""
        if hasattr(self, "qs"):
            return self.qs
        self.qs = Attachment.objects.filter(
            registration=self.registration,
        )
        return self.qs

    def get_segments(self):
        # We still need this segment for easy rendering inside the
        # custom form template
        return self._fields_to_segments(
            []
        )


class NewAttachmentQuestion(
        RegistrationQuestionMixin,
        questions.Question,
):

    class Meta:
        model = Attachment
        fields = [
            "description",
            "upload",
        ]

    def get_segments(self):
        return self._fields_to_segments(
            self.Meta.fields,
        )

    def get_queryset(self):
        """Return the list of receivers currently connected to
        this registration."""
        if hasattr(self, "qs"):
            return self.qs
        self.qs = Attachment.objects.filter(
            registration=self.registration,
        )
        return self.qs

    def get_create_url(self):
        return reverse(
            "registrations:edit_question",
            kwargs={
                "question": self.slug,
                "reg_pk": self.blueprint.object.pk,
            },
        )

    def get_delete_url(self):
        return reverse(
            "registrations:delete_attachment",
            kwargs={
                "reg_pk": self.blueprint.object.pk,
                "attachment_pk": self.get_object().pk,
            }
        )
