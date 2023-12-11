from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.template import loader, Template

from cdh.core import forms as cdh_fields
from cdh.questions import questions
from registrations.models import Registration, Response

from .helpers import RegistrationQuestionMixin

class NewResponseQuestion(
        RegistrationQuestionMixin,
        questions.Question,
):
    """Question that creates a new response and adds them to a registration"""

    class Meta:
        model = Response
        fields = [
            'comments',
            'approved',
        ]
    slug = "new_response"
    model = Meta.model

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = kwargs.get('user')
        kwargs.pop('user')

    # def get_create_url(self):
    #     return reverse(
    #         "registrations:edit_question",
    #         kwargs={
    #             "question": "new_receiver",
    #             "reg_pk": self.blueprint.object.pk,
    #         },
    #     )

    # def get_delete_url(self):
    #     return reverse(
    #         "registrations:delete_receiver",
    #         kwargs={
    #             "reg_pk": self.get_registration().pk,
    #             "receiver_pk": self.instance.pk,
    #         }
    #     )

    def get_success_url(self):
        return reverse(
            "registrations:response",
            )

    def get_segments(self):
        return self._fields_to_segments(
            self.fields
        )

    def save(self):
        self.instance.registration = self.get_registration()
        self.instance.created_by = self.user
        return super().save()