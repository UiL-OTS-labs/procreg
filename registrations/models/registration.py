from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext as _

# Create your models here.

USER_MODEL = get_user_model()


class Registration(models.Model):
    
    YES_NO = (
        ('yes', "models:choices:yes"),
        ('no', "models:choices:no"),
    )
    YES_NO_NA = (
        ('yes', "models:choices:yes"),
        ('no', "models:choices:no"),
        ('non_applicable', "models:choices:non_applicable"),
    )

    title = models.CharField(max_length=200,
                             help_text="models:registration_title_help_text",
                             )
    created_by = models.ForeignKey(USER_MODEL,
                                   on_delete=models.SET_DEFAULT,
                                   related_name="registrations_created",
                                   blank=True,
                                   null=True,
                                   default=None,
                                   )
    created_on = models.DateTimeField(auto_now=True)
    applicants = models.ManyToManyField(USER_MODEL,
                                        related_name="applicant_for",
                                        blank=True,
                                        )
    faculty = models.CharField(max_length=100,
                               blank=True,
                               default=None,
                               null=True,
                               )
    uses_information = models.BooleanField(
        blank=True,
        null=True,
        choices=(
            (False, _("models:registration:registration_uses_information_false")),
            (True, _("models:registration:registration_uses_information_true")),
             )
        )
    date_start = models.DateField(blank=True,
                                  null=True,
                                  )
    date_end = models.DateField(blank=True,
                                null=True,
                                )
    confirm_submission = models.BooleanField(
        default=False,
        choices=(
            (False, _("models:registration:confirm_submission_false")),
            (True, _("models:registration:confirm_submission_true")),
             )
        )

    involves_consent = models.BooleanField(
        default=False,
        )
    involves_non_consent = models.BooleanField(
        default=False,
        )
    involves_guardian_consent = models.BooleanField(
        default=False,
        )
    involves_other_people = models.BooleanField(
        default=False,
        )
    # Storage question
    # These are charfields for future-proofing and consistency
   
    data_storage = models.CharField(
        max_length=25,
        choices=YES_NO,
        default="",
        )
    consent_document_storage = models.CharField(
        max_length=25,
        choices=YES_NO_NA,
        default="",
        )
    multimedia_storage = models.CharField(
        max_length=25,
        choices=YES_NO_NA,
        default="",
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
