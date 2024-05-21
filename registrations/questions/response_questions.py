from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.template import loader, Template

from cdh.core import forms as cdh_fields
from cdh.questions import questions
from registrations.models import Response

from .helpers import RegistrationQuestionMixin


class PoResponseQuestion(
    RegistrationQuestionMixin,
    questions.Question,
):
    """Question that creates a new PO response and
    adds them to a registration"""

    class Meta:
        model = Response
        fields = [
            "comments",
            "status",
        ]

    title = _("questions:response:po_response")
    description = Template(_("questions:response:po_response_desc"))
    slug = "po_response"
    model = Meta.model
    is_editable = True

    def __init__(self, *args, **kwargs):
        if 'user' in kwargs:
            self.user = kwargs.pop("user")
        super().__init__(*args, **kwargs)

    def get_segments(self):
        return self._fields_to_segments(self.fields)

    def save(self):
        registration = self.get_registration()
        self.instance.registration = registration
        self.instance.created_by = self.user
        self.instance.type = "PO"
        return super().save()


class UserResponseQuestion(
    RegistrationQuestionMixin,
    questions.Question,
):
    """Question that creates a new user response and
    adds them to a registration"""

    class Meta:
        model = Response
        fields = [
            "comments",
        ]

    title = _("questions:response:user_response")
    description = Template(_("questions:response:user_response_desc"))
    slug = "user_response"
    model = Meta.model
    is_editable = True

    def __init__(self, *args, **kwargs):
        if 'user' in kwargs:
            self.user = kwargs.pop("user")
        super().__init__(*args, **kwargs)

    def get_segments(self):
        return self._fields_to_segments(self.fields)

    def save(self):
        registration = self.get_registration()
        self.instance.registration = registration
        self.instance.created_by = self.user
        self.instance.type = "USER"
        self.instance.status = "submitted"
        return super().save()
