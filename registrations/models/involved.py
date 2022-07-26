from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext as _

from . import Registration

# Create your models here.

USER_MODEL = get_user_model()

class Involved(models.Model):

    TYPES = (
        ('consent', _("models:involved:consent")),
        ('non_consent', _("models:involved:non_consent")),
        ('guardian_consent', _("models:involved:guardian")),
        ('other', _("models:involved:other")),
    )

    type = models.CharField(
        max_length=25,
        choices=TYPES,
    )
    registration = models.ForeignKey(
        to=Registration,
        on_delete=models.CASCADE,
        related_name='involved_groups',
        )
