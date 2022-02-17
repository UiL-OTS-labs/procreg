from django.utils.translation import ugettext_lazy as _
from django import forms
from django.urls import reverse

from uil.questions import questions
from .models import Registration, ParticipantCategory



class RegistrationQuestionMixin:

    def get_edit_url(self):

        if not hasattr(self.instance, 'registration'):
            self.instance.registration = self.instance

        return reverse(
            'registrations:edit_question',
            kwargs={
                'question': self.slug,
                'question_pk': self.instance.pk,
                'reg_pk': self.instance.registration.pk,
            }
        )


class NewRegistrationQuestion(RegistrationQuestionMixin,
        questions.Question,):

    title = _("registrations:forms:registration_title")
    model = Registration
    slug = 'new_reg'
    is_editable = True

    class Meta:
        model = Registration
        fields = [
            'title',
        ]

    def get_segments(self):

        segments = []
        segments.append(self._field_to_segment('title'))

        return segments

class FacultyQuestion(RegistrationQuestionMixin, questions.Question):

    class Meta:
        model = Registration
        fields = [
            'faculty',
        ]

    title = _("registrations:forms:faculty_question_title")
    model = Registration
    slug = "faculty"
    is_editable = True


    def get_segments(self):

        segments = []
        segments.append(self._field_to_segment('faculty'))

        return segments


class CategoryQuestion(RegistrationQuestionMixin, questions.Question):

    class Meta:
        model = ParticipantCategory
        fields = [
            'name',
            'number',
            'has_consented',
        ]

    is_editable = True
    slug = "category"
    model = ParticipantCategory




Q_LIST = [NewRegistrationQuestion,
          FacultyQuestion,
          ]

QUESTIONS = {q.slug: q for q in Q_LIST}
