from cdh.questions import questions
from .helpers import TemplatedFormMixin, RegistrationQuestionMixin
from registrations.models import Registration, Receiver, Attachment
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.template import Template

class AttachmentsQuestion(
        TemplatedFormMixin,
        RegistrationQuestionMixin,
        questions.Question,
):
    # Django ModelForm compatibility
    class Meta:
        model = Registration
        fields = [
        ]
    # Procreg question stuff
    model = Meta.model
    title = _("questions:attachments:question_title")
    description = Template(_("questions:attachments:question_description"))
    slug = "attachments"
    is_editable = True
    show_progress = True
    # Custom template for Manager inclusion
    template_name = "forms/attachments_form.html"
    use_custom_template = True

    def get_queryset(self):
        """Return the list of attachments currently connected to
        this registration."""
        if hasattr(self, "qs"):
            return self.qs
        self.qs = Attachment.objects.filter(
            registration=self.get_registration(),
        )
        return self.qs

    def get_form_context(self):
        context = super().get_form_context()
        existing = self.blueprint.get_question(
            "new_attachment",
            question_pk=True,
            always_list=True,
        )
        new = self.blueprint.get_question(
            "new_attachment",
            question_pk=None,
        )
        context.update(
            {
                "existing": existing,
                "new": new,
            }
        )
        return context

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

    slug = "new_attachment"
    model = Attachment
    title = _("registrations:questions:new_attachment")

    class Meta:
        model = Attachment
        fields = [
            "file_description",
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

    def get_success_url(self):
        return reverse(
            "registrations:edit_question",
            kwargs={
                "reg_pk": self.get_registration().pk,
                "question": "attachments",
                "question_pk": self.get_registration().pk,
            }
        )

    def save(self):
        self.instance.registration = self.get_registration()
        return super().save()
