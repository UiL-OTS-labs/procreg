from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.template import loader, Template

from cdh.core import forms as cdh_fields
from cdh.questions import questions
from registrations.models import Registration, ParticipantCategory, Receiver, Software

from .helpers import RegistrationQuestionMixin


class NewRegistrationQuestion(
        RegistrationQuestionMixin,
        questions.Question,
):
    title = _("questions:new_reg:question_title")
    description = Template(_("registrations:forms:registration_description"))
    model = Registration
    slug = 'new_reg'
    is_editable = True

    class Meta:
        model = Registration
        fields = [
            'registration_title',
        ]

    fields = Meta.fields
    model = Meta.model

    def get_segments(self):

        segments = []
        segments.append(self._field_to_segment('registration_title'))

        return segments


class FacultyQuestion(
        RegistrationQuestionMixin,
        questions.Question
):

    show_progress = True
    
    class Meta:
        model = Registration
        fields = [
            'faculty',
        ]

    title = _("questions:faculty:question_title")
    description = Template(_("questions:faculty:question_description"))
    model = Registration
    slug = "faculty"
    is_editable = True
    
    def get_segments(self):
        segments = []
        segments.append(self._field_to_segment('faculty'))
        self.segments = segments
        return segments


class TraversalQuestion(RegistrationQuestionMixin, questions.Question):

    show_progress = True

    class Meta:
        model = Registration
        fields = [
            'date_start',
            'date_end',
        ]
        widgets = {
            'date_end': cdh_fields.DateInput,
            'date_start': cdh_fields.DateInput,
        }

    title = _("questions:traversal:question_title")
    description = Template(
        _("questions:traversal:question_description")
    )
    model = Registration
    slug = "traversal"
    is_editable = True

    def get_segments(self):
        segments = []
        segments.append(self._field_to_segment('date_start'))
        segments.append(self._field_to_segment('date_end'))
        return segments


class GoalQuestion(RegistrationQuestionMixin, questions.Question):

    show_progress = True

    class Meta:
        model = Registration
        fields = [
            "research_goal",
        ]

    title = _("questions:goal:question_title")
    description = Template(_("questions:goal:question_description"))
    model = Registration
    slug = "goal"
    is_editable = True

    def get_segments(self):
        segments = []
        segments.append(self._field_to_segment('research_goal'))
        return segments


class UsesInformationQuestion(RegistrationQuestionMixin, questions.Question):

    class Meta:
        model = Registration
        fields = [
            'uses_information',
        ]

    title = _("registrations:forms:uses_information_question_title")
    description = Template(_("registrations:forms:uses_information_question_title"))
    model = Registration
    slug = "uses_information"
    is_editable = True
    show_progress = False

    def get_segments(self):

        segments = []
        segments.append(self._field_to_segment('uses_information'))

        return segments


class ConfirmInformationUseQuestion(RegistrationQuestionMixin, questions.Question):

    class Meta:
        model = Registration
        fields = [
            #'uses_information',
        ]

    title = _("registrations:forms:confirm_information_use_question_title")
    description = Template(_("registrations:forms:confirm_information_use_question_title"))
    model = Registration
    slug = "confirm_information_use"
    is_editable = False
    show_progress = True

    def get_segments(self):

        segments = []
        content = questions.Segment()
        content.type = "paragraph"
        content.paragraph = self.description
        segments.append(content)
        return segments

    def get_success_url(self):
        return reverse(
            "registrations:summary",
            kwargs={
                'reg_pk': self.get_registration().pk,
            }
        )




class RetentionQuestion(
        RegistrationQuestionMixin,
        questions.Question,
):

    class Meta:
        model = Registration
        fields = [
            "raw_storage_location",
            "raw_data_decade",
            "ic_storage_location",
            "ic_storage_decade",
            "audio_video_kept",
            "audio_video_kept_details",
        ]

    title = _("questions:retention:question_title")
    description = Template(_("questions:retention:question_description"))
    model = Meta.model
    slug = "retention"
    is_editable = True
    show_progress = True

    def get_segments(self):

        return self._fields_to_segments(
            fields_list=self.Meta.fields,
        )


class ReceiverQuestion(RegistrationQuestionMixin, questions.Question):
    # Django ModelForm compatibility
    class Meta:
        model = Registration
        fields = [
            "third_party_sharing",
        ]
    # Procreg question stuff
    model = Meta.model
    title = _("questions:receivers:question_title")
    description = Template(_("questions:receivers:question_description"))
    slug = "receivers"
    is_editable = True
    show_progress = True
    # Custom template for Manager inclusion
    template_name = "forms/receiver_form.html"
    use_custom_template = True

    def get_queryset(self):
        """Return the list of receivers currently connected to
        this registration."""
        if hasattr(self, "qs"):
            return self.qs
        self.qs = Receiver.objects.filter(
            registration=self.registration,
        )
        return self.qs

    def render(self, context={}):
        """This is kind of silly, but I want to implement custom form
        template  as closely as possible to the django 4 way so the
        upgrade path is easy."""
        if not self.use_custom_template:
            return super().render()
        template = loader.get_template(self.template_name)
        context.update(
            {
                "question": self,
                "editing": True,
            }
        )
        if self.instance.third_party_sharing == "yes":
            new = self.blueprint.get_question(
                slug="new_receiver",
                question_pk=None,
            )
            context.update(
                {
                    "source_question": new,
                    "show_selector": True,
                }
            )
        return template.render(context.flatten())

    def get_segments(self):
        # We still need this segment for easy rendering inside the
        # custom form template
        return self._fields_to_segments(
            ["third_party_sharing", ]
        )


class NewReceiverQuestion(
        RegistrationQuestionMixin,
        questions.Question,
):
    """Question that creates new receivers and adds them to a registration"""

    class Meta:
        model = Receiver
        fields = [
            "name",
            "outside_eer",
            "basis_for_transfer",
            "explanation",
        ]
    slug = "new_receiver"
    model = Meta.model

    def __init__(self, *args, **kwargs):
        """Remove unnecessary fields of inside EER"""
        super().__init__(*args, **kwargs)
        if self.instance.outside_eer != "yes":
            self.fields.pop("basis_for_transfer")
            self.fields.pop("explanation")

    def get_existing(self):
        """Return the list of receivers currently connected to
        this registration."""
        return self.blueprint.get_question(
            slug="new_receiver",
            question_pk=True,
            always_list=True,
        )

    def get_create_url(self):
        return reverse(
            "registrations:edit_question",
            kwargs={
                "question": "new_receiver",
                "reg_pk": self.blueprint.object.pk,
            },
        )

    def get_delete_url(self):
        return reverse(
            "registrations:delete_receiver",
            kwargs={
                "reg_pk": self.get_registration().pk,
                "receiver_pk": self.instance.pk,
            }
        )

    def get_success_url(self):
        return reverse(
            "registrations:edit_question",
            kwargs={
                "reg_pk": self.get_blueprint().object.pk,
                "question": "receivers",
                "question_pk": self.get_blueprint().object.pk,
            })

    def get_segments(self):
        return self._fields_to_segments(
            self.fields
        )

    def save(self):
        self.instance.registration = self.get_registration()
        return super().save()


class SoftwareQuestion(
        RegistrationQuestionMixin,
        questions.Question,
):
    class Meta:
        model = Registration
        fields = [
            "uses_software",
        ]
    slug = "software"
    description = Template(_("questions:software:question_description"))
    title = _("questions:software:question_title")
    model = Meta.model
    # Custom template for Manager inclusion
    template_name = "forms/software_form.html"
    use_custom_template = True

    def render(self, context={}):
        """This is kind of silly, but I want to implement custom form
        template  as closely as possible to the django 4 way so the
        upgrade path is easy."""
        if not self.use_custom_template:
            return super().render()
        template = loader.get_template(self.template_name)
        context.update(
            {
                "question": self,
                "editing": True,
            }
        )
        if self.instance.uses_software == "yes":
            existing = self.blueprint.get_question(
                always_list=True,
                slug="new_software",
                question_pk=True,
            )
            new = self.blueprint.get_question(
                slug="new_software",
                question_pk=None,
            )
            context.update(
                {
                    "source_question": new,
                    "show_selector": True,
                }
            )
        return template.render(context.flatten())

    def get_segments(self):
        # We still need this segment for easy rendering inside the
        # custom form template
        return self._fields_to_segments(
            ["uses_software", ]
        )


class NewSoftwareQuestion(
        RegistrationQuestionMixin,
        questions.Question,
):
    """Question that creates new softwares and adds them to a registration"""

    class Meta:
        model = Software
        fields = [
            "name",
            "not_approved",
        ]
    slug = "new_software"
    model = Meta.model

    def get_existing(self):
        """Return the list of receivers currently connected to
        this registration."""
        return self.blueprint.get_question(
            slug=self.slug,
            question_pk=True,
            always_list=True,
        )

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
            "registrations:delete_software",
            kwargs={
                "reg_pk": self.get_registration().pk,
                "software_pk": self.instance.pk,
            }
        )

    def get_success_url(self):
        return reverse(
            "registrations:edit_question",
            kwargs={
                "reg_pk": self.get_blueprint().object.pk,
                "question": "software",
                "question_pk": self.get_blueprint().object.pk,
            })

    def get_segments(self):
        return self._fields_to_segments(
            self.fields
        )

    def save(self):
        self.instance.registration = self.get_registration()
        return super().save()


class SecurityQuestion(
        RegistrationQuestionMixin,
        questions.Question,
):
    class Meta:
        model = Registration
        fields = [
            "follows_policy",
            "policy_exceptions",
            "policy_additions",
        ]
    model = Meta.model
    slug = "security"
    description = Template(_("questions:security:question_description"))
    title = _("questions:security:question_title")

    def get_segments(self):
        return self._fields_to_segments(self.fields)



class SubmitQuestion(RegistrationQuestionMixin, questions.Question):

    class Meta:
        model = Registration
        fields = [
            'confirm_submission',
        ]

    title = _("registrations:forms:submit_question_title")
    description = Template(_("registrations:forms:submit_question_description"))
    model = Registration
    slug = "submit"
    is_editable = False
    show_progress = False

    def get_segments(self):

        segments = []

        segments.append(
            self._field_to_segment(
                "uses_information"
            )
        )
        
        content = questions.Segment()
        content.type = "paragraph"
        content.paragraph = _("registrations:forms:confirm_information_use_paragraph")
        segments.append(content)

        return segments


    
class CategoryQuestion(RegistrationQuestionMixin, questions.Question):

    show_progress = True
    
    class Meta:
        model = ParticipantCategory
        fields = [
            'name',
            'number',
            'has_consented',
        ]

    title = "registrations:forms:category_question_title"
    description = Template(_("registrations:forms:category_question_description"))
    is_editable = True
    slug = "category"
    model = ParticipantCategory

    def get_segments(self):

        segments = []
        segments.append(self._field_to_segment('name'))
        segments.append(self._field_to_segment('number'))
        segments.append(self._field_to_segment('has_consented'))
        return segments

    def save(self, *args, **kwargs):

        reg = Registration.objects.get(pk=self.reg_pk)
        self.instance.registration = reg
        return super().save(*args, **kwargs)

