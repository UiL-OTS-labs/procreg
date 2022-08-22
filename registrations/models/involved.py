from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext as _

from . import Registration

# Create your models here.

USER_MODEL = get_user_model()


class Involved(models.Model):

    registration_related_name = "involved_groups"

    GROUP_TYPES = (
        ('consent', _("models:involved:consent")),
        ('non_consent', _("models:involved:non_consent")),
        ('guardian_consent', _("models:involved:guardian")),
        ('other', _("models:involved:other")),
    )

    group_type = models.CharField(
        max_length=25,
        choices=GROUP_TYPES,
    )
    name = models.CharField(
        max_length=200,
        default="",
    )
    registration = models.ForeignKey(
        to=Registration,
        on_delete=models.CASCADE,
        related_name='involved_groups',
    )
    process_purpose = models.TextField(
        max_length=500,
        default="",
    )
