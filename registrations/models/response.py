from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext as _
from registrations.models import Registration


USER_MODEL = get_user_model()


class Response(models.Model):
    STATUSES = (
        ("draft", "models:response:status_draft"),
        ("submitted", "models:response:status_submitted"),
        ("registered", "models:response:status_registered"),
    )

    status = models.CharField(
        max_length=20,
        choices=STATUSES,
        default="draft",
        help_text=_("models:response:status_help_text"),
        verbose_name=_("models:response:status_verbose_name"),
    )

    comments = models.CharField(
        max_length=1000,
        help_text=_("models:response:comments_help_text"),
        verbose_name=_("models:response:comments_verbose_name"),
        default="",
        blank=True,
    )

    created_by = models.ForeignKey(
        USER_MODEL,
        on_delete=models.SET_DEFAULT,
        related_name="responses_created",
        blank=True,
        null=True,
        default=None,
    )

    registration = models.ForeignKey(
        Registration,
        on_delete=models.CASCADE,
    )

    RESPONSE_TYPES = (
        ("PO", "PO Response"),
        ("USER", "User Response"),
    )

    type = models.CharField(
        max_length=20,
        choices=RESPONSE_TYPES,
        blank=True,
        default="",
    )
