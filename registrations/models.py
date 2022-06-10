from django.db import models
from django.contrib.auth import get_user_model

# Create your models here.

USER_MODEL = get_user_model()


class Registration(models.Model):

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
    date_start = models.DateField(blank=True,
                                  null=True,
                                  )
    date_end = models.DateField(blank=True,
                                null=True,
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
