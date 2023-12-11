from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext as _
from .registration import YES_NO, YES_NO_NA, Registration


USER_MODEL = get_user_model()


class Response(models.Model):
    approved = models.BooleanField(
        help_text=_("models:response:approved_help_text"),
        verbose_name=_("models:response:approved_verbose_name"),
    )

    comments = models.CharField(
        max_length=1000,
        help_text=_("models:response:comments_help_text"),
        verbose_name=_("models:response:comments_verbose_name"),
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
