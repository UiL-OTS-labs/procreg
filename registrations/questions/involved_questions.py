from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from cdh.questions import questions

from registrations.models import Registration, Involved
from .helpers import RegistrationQuestionMixin, QuestionViewArgumentsMixin

class InvolvedPeopleQuestion(
        RegistrationQuestionMixin,
        questions.Question,
):

    class Meta:
        model = Registration
        fields = [
            'involves_consent',
            'involves_non_consent',
            'involves_guardian_consent',
            'involves_other_people',
        ]

    title = _("registrations:forms:involved_people_question_title")
    description = _("registrations:forms:involved_people_question_description")
    model = Meta.model
    slug = "involved_people"
    is_editable = True
    show_progress = True

    def get_segments(self):

        return self._fields_to_segments(
            fields_list=self.Meta.fields,
        )

class NewInvolvedQuestion(
        QuestionViewArgumentsMixin,
        RegistrationQuestionMixin,
        questions.Question,
):
    class Meta:
        model = Involved
        fields = [
            'name',
        ]

    is_editable = True
    slug = "new_involved"
    title = _("registrations:forms:involved:new_title")
    description = _("registrations:forms:involved:new_description")
    model = Meta.model
    view_arguments = ["group_type"]

    def __init__(self, *args, **kwargs):
        "Look for a group type in kwargs or alternatively given instance."

        self.group_type = kwargs.pop("group_type", None)
        if not self.group_type:
            if "instance" in kwargs.keys():
                self.group_type = kwargs["instance"].group_type
        return super().__init__(*args, **kwargs)

    def get_segments(self):
        type_paragraph = questions.Segment(
            type="paragraph",
            paragraph=f"Type: {self.group_type}",
        )

        return [type_paragraph] + self._fields_to_segments(
            fields_list=self.Meta.fields,
        )

    def get_edit_url(self):

        registration = self.get_registration()

        reverse_kwargs = {
            "reg_pk": registration.pk,
            "question": self.slug,
        }

        if self.instance.pk:  # Edit existing model
            reverse_kwargs['question_pk'] = self.instance.pk
        else:  # Else, make sure we know what type to create
            reverse_kwargs['group_type'] = self.instance.group_type

        return reverse(
            "registrations:edit_question",
            kwargs=reverse_kwargs,
        )
    
    def get_success_url(self):
        return reverse(
            "registrations:involved_manager",
            kwargs={
                "reg_pk": self.get_blueprint().object.pk,
            })

    def save(self, *args, **kwargs):
        "Set a registration and group type on creation."
        self.instance.registration = self.blueprint.object
        return super().save(*args, **kwargs)
    

class PurposeQuestion(RegistrationQuestionMixin,
                      questions.Question,
                      ):

    class Meta:
        model = Involved
        fields = [
            "process_purpose",
        ]

    title = _("registrations:forms:purpose_question_title")
    description = _("registrations:forms:purpose_question_description")
    model = Meta.model
    slug = "purpose"
    is_editable = True
    show_progress = True

    def get_segments(self):

        return self._fields_to_segments(
            fields_list=self.Meta.fields,
        )


class SpecialDetailsQuestion(
        RegistrationQuestionMixin,
        questions.Question,
):

    class Meta:
        model = Involved
        fields = [
            "special_details",
            "gave_explicit_permission",
            "explicit_permission_details",
            "grounds_for_exception",
            "algemeen_belang_details",
            "legal_grounds_details",
        ]

    title = _("registrations:special_details_title")
    description = _("registrations:forms:special_details_description")
    model = Meta.model
    slug = "special_details"
    is_editable = True
    show_progress = True

    def get_segments(self):

        return self._fields_to_segments(
            fields_list=self.Meta.fields,
        )


class SensitiveDetailsQuestion(
        RegistrationQuestionMixin,
        questions.Question,
):

    class Meta:
        model = Involved
        fields = [
            "provides_criminal_information",
            "involves_children_under_15",
            "other_sensitive_details",
            "provides_no_sensitive_details",
        ]

    title = _("registrations:sensitive_details_title")
    description = _("registrations:forms:sensitive_details_description")
    model = Meta.model
    slug = "sensitive_details"
    is_editable = True
    show_progress = True

    def get_segments(self):

        return self._fields_to_segments(
            fields_list=self.Meta.fields,
        )


class RegularDetailsQuestion(
        RegistrationQuestionMixin,
        questions.Question,
):

    class Meta:
        model = Involved
        fields = [
            "regular_details",
            "provides_ic_form",
            "ic_form_details",
            "extra_details",
        ]

    title = _("registrations:regular_details_title")
    description = _("registrations:forms:regular_details_description")
    model = Meta.model
    slug = "regular_details"
    is_editable = True
    show_progress = True

    def get_segments(self):

        return self._fields_to_segments(
            fields_list=self.Meta.fields,
        )
