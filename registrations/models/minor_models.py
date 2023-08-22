from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext as _
from .registration import YES_NO, YES_NO_NA, Registration

# Create your models here.

USER_MODEL = get_user_model()


class Receiver(models.Model):

    TRANSFER_BASES = (
        ("explicit_permission", "models:receiver:explicit_permission"),
        ("adequacy_decision", "models:receiver:adequacy_decision"),
        ("standard_contractual", "models:receiver:standard_contractual"),
        ("other", "models:receiver:other"),
        ("no_basis", "models:receiver:no_basis"),
        ("", "models:choices:please_specify"),
    )
    name = models.CharField(
        max_length=200,
        default="",
    )
    outside_eer = models.CharField(
        max_length=10,
        choices=YES_NO,
    )
    basis_for_transfer = models.CharField(
        max_length=200,
        choices=TRANSFER_BASES,
        default="",
    )
    explanation = models.TextField(
        max_length=2000,
        default="",
    )
    registration = models.ForeignKey(
        Registration,
        related_name="receivers",
        on_delete=models.CASCADE,
    )


class Software(models.Model):

    name = models.CharField(
        max_length=200,
        blank=True,
        default="",
    )
    not_approved = models.CharField(
        max_length=10,
        choices=YES_NO,
        null=True,
        blank=True,
    )
    registration = models.ForeignKey(
        Registration,
        related_name="software",
        on_delete=models.CASCADE,
    )


class Attachment(models.Model):

    file_description = models.CharField(
        max_length=500,
        blank=True,
        default=""
    )
    upload = models.FileField(
    )
    registration = models.ForeignKey(
        Registration,
        related_name="attachments",
        on_delete=models.CASCADE,
    )

class ParticipantCategory(models.Model):

    name = models.CharField(max_length=100,
                            blank=True,
                            null=True,
                            )
    number = models.PositiveIntegerField(blank=True,
                                         null=True,
                                         )
    has_consented = models.BooleanField(default=False)
    registration = models.ForeignKey(Registration,
                                     on_delete=models.CASCADE,
                                     )
