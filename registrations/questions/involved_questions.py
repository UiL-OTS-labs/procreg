from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.template import Template

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
            'involves_knowingly',
            'involves_not_knowingly',
            'involves_guardian',
            'involves_other',
        ]

    title = _("questions:involved_people:question_title")
    description = Template(_("questions:involved_people:question_description"))
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
    title = _("questions:new_involved:question_title")
    description = Template(_("questions:new_involved:question_description"))
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

    title = _("questions:purpose:question_title")
    description = Template(_("questions:purpose:question_description"))
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

    title = _("questions:special_details:question_title")
    description = Template(_("questions:special_details:question_description"))
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

    title = _("questions:sensitive_details:question_title")
    description = Template(_("questions:sensitive_details:question_description"))
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

    description = Template(
        _("questions:regular_details:question_description")
    )
    title = _("questions:regular_details:question_title")
    model = Meta.model
    slug = "regular_details"
    is_editable = True
    show_progress = True

    def __init__(self, *args, **kwargs):
        """
        Include involved group name in description if an instance
        is provided.
        """
        super().__init__(*args, **kwargs)
        if hasattr(self, "instance"):
            self.description = Template(
                _("questions:regular_details:question_description")
                + " " + _("global:possessive_preposition") + " "
                + self.instance.name
            )

    def get_segments(self):

        return self._fields_to_segments(
            fields_list=self.Meta.fields,
        )
