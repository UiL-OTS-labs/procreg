from django.utils.translation import ugettext_lazy as _
from django.urls import reverse
from django.template import loader

from cdh.questions import questions
from .models import Registration, ParticipantCategory, Involved, Receiver, Software
from .progress import ProgressItemMixin


class RegistrationQuestionMixin(ProgressItemMixin):

    show_progress = True
    extra_form_kwargs = []

    def __init__(self, *args, **kwargs):
        self.blueprint = kwargs.pop("blueprint", None)
        self.registration = kwargs.pop('registration', None)
        self.view_kwargs = kwargs.pop('view_kwargs', None)
        return super().__init__(*args, **kwargs)

    def get_registration(self):
        if not getattr(self, "registration"):
            self.registration = self.blueprint.object
        return self.registration

    def get_blueprint(self):
        return self.blueprint

    def get_edit_url(self):

        reverse_kwargs = {
            'question': self.slug,
            'question_pk': self.instance.pk,
            'reg_pk': self.get_registration().pk,
        }

        if reverse_kwargs["question_pk"] is None:
            reverse_kwargs.pop("question_pk")

        return reverse(
            'registrations:edit_question',
            kwargs=reverse_kwargs,
        )


class PlaceholderQuestion(RegistrationQuestionMixin, questions.Question):
    title = "Placeholder"
    description = "Description of placeholder question"
    is_editable = True

    class Meta:
        model = Registration
        fields = []

    def __init__(self, slug="placeholder", *args, **kwargs):
        super().__init__(self)
        self.slug = slug
        self.disabled = True

    def get_edit_url(self):
        return False


class NewRegistrationQuestion(
        RegistrationQuestionMixin,
        questions.Question,
):
    title = _("registrations:forms:registration_title")
    description = _("registrations:forms:registration_description")
    model = Registration
    slug = 'new_reg'
    is_editable = True

    class Meta:
        model = Registration
        fields = [
            'title',
        ]

    fields = Meta.fields
    model = Meta.model

    def get_segments(self):

        segments = []
        segments.append(self._field_to_segment('title'))

        return segments


class FacultyQuestion(RegistrationQuestionMixin, questions.Question):

    show_progress = True
    
    class Meta:
        model = Registration
        fields = [
            'faculty',
        ]

    title = _("registrations:forms:faculty_question_title")
    description = _("registrations:forms:faculty_question_description")
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

    title = _("registrations:forms:traversal_question_title")
    description = _("registrations:forms:traversal_question_description")
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

    title = _("registrations:forms:goal_question_title")
    description = _("registrations:forms:goal_question_description")
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
    description = _("registrations:forms:uses_information_question_title")
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
    description = _("registrations:forms:confirm_information_use_question_title")
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


class InvolvedPeopleQuestion(RegistrationQuestionMixin,
                             questions.Question,):

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


class QuestionViewArgumentsMixin():
    """Use this mixin to receive arguments from the calling view"""

    view_arguments = []

    def __init__(self, *args, **kwargs):
        for arg_name in self.view_arguments:
            arg_value = kwargs.pop("arg_name", None)
            setattr(self, arg_name, arg_value)
        return super().__init__(*args, **kwargs)


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
            "other_regular_details",
            "provides_ic_form",
            "ic_form_details",
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

    title = _("registrations:forms:storage_question_title")
    description = _("registrations:forms:storage_question_description")
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
    title = _("registrations:forms:receiver_question_title")
    description = _("registrations:forms:receiver_question_description")
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
            "new_receiver",
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
    description = _("questions:software:description")
    title = _("questions:software:title")
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
            self.slug,
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
        breakpoint()
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
    slug = "security"
    description = _("questions:security:description")
    title = _("questions:security:title")


class SubmitQuestion(RegistrationQuestionMixin, questions.Question):

    class Meta:
        model = Registration
        fields = [
            'confirm_submission',
        ]

    title = _("registrations:forms:submit_question_title")
    description = _("registrations:forms:submit_question_description")
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
    description = "registrations:forms:category_question_description"
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



Q_LIST = [
    NewRegistrationQuestion,
    FacultyQuestion,
    CategoryQuestion,
    TraversalQuestion,
    UsesInformationQuestion,
    ConfirmInformationUseQuestion,
    InvolvedPeopleQuestion,
    RetentionQuestion,
    NewInvolvedQuestion,
    GoalQuestion,
    PurposeQuestion,
    NewSoftwareQuestion,
    SoftwareQuestion,
]

QUESTIONS = {q.slug: q for q in Q_LIST}
