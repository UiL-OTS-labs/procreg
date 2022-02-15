from django.utils.translation import ugettext_lazy as _
from django import forms
from django.urls import reverse

from uil.questions import questions
from .models import Registration



class RegistrationQuestionMixin:

    def get_edit_url(self):

        if not hasattr(self.instance, 'track'):
            self.instance.track = self.instance

        return reverse(
            'tracks:edit_question',
            kwargs={
                'question': self.slug,
                'question_pk': self.instance.pk,
                'track_pk': self.instance.track.pk,
            }
        )


class NewRegistrationQuestion(RegistrationQuestionMixin,
        questions.Question,):

    title = _("registrations:forms:registration_title")
    model = Registration
    slug = 'new_track'
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


QUESTIONS = {'new_registration': NewRegistrationQuestion}
