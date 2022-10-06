from django.utils.translation import ugettext_lazy as _
from django import forms
from django.urls import reverse

from cdh.questions import questions
from .models import Registration, ParticipantCategory, Involved


class RegistrationQuestionMixin:

    show_progress = True

    def __init__(self, *args, **kwargs):
        self.registration = kwargs.pop('registration', None)
        self.view_kwargs = kwargs.pop('view_kwargs', None)
        return super().__init__(*args, **kwargs)

    def get_registration(self):
        self.registration = self.question_data.get("registration")
        # Hack for debugging and creating a new registration
        if not self.registration:
            self.registration = Registration()
        return self.registration

    def get_edit_url(self):

        registration = self.get_registration()

        if not hasattr(self.instance, 'registration'):
            self.instance.registration = registration

        reverse_kwargs = {
            'question': self.slug,
            'question_pk': self.instance.pk,
            'reg_pk': registration.pk,
        }

        if reverse_kwargs["question_pk"] is None:
            reverse_kwargs.pop("question_pk")

        return reverse(
            'registrations:edit_question',
            kwargs=reverse_kwargs,
        )

#    def instantiate_from_blueprint(blueprint):

#        return super()(instance=blueprint.registration)


class NewRegistrationQuestion(RegistrationQuestionMixin,
        questions.Question,):

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


class NewInvolvedQuestion(RegistrationQuestionMixin,
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
            reverse_kwargs['group_type'] = self.group_type

        return reverse(
            "registrations:edit_question",
            kwargs=reverse_kwargs,
        )

    def save(self, *args, **kwargs):
        "Set a registration and group type on creation."
        self.instance.registration = self.registration
        self.instance.group_type = self.group_type
        return super().save(*args, **kwargs)


class StorageQuestion(RegistrationQuestionMixin,
                      questions.Question,
                      ):

    class Meta:
        model = Registration
        fields = [
            "data_storage",
            "consent_document_storage",
            "multimedia_storage",
        ]

    title = _("registrations:forms:storage_question_title")
    description = _("registrations:forms:storage_question_description")
    model = Meta.model
    slug = "storage"
    is_editable = True
    show_progress = True

    def get_segments(self):

        return self._fields_to_segments(
            fields_list=self.Meta.fields,
        )

    
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



Q_LIST = [NewRegistrationQuestion,
          FacultyQuestion,
          CategoryQuestion,
          TraversalQuestion,
          UsesInformationQuestion,
          ConfirmInformationUseQuestion,
          InvolvedPeopleQuestion,
          StorageQuestion,
          NewInvolvedQuestion,
          ]

QUESTIONS = {q.slug: q for q in Q_LIST}
