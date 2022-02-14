from django.db import models
from django.contrib.auth import get_user_model

# Create your models here.

USER_MODEL = get_user_model()


class Registration(models.Model):

    title = models.CharField(max_length=200,
                             help_text="models:registration_title_help_text",
                             )
    created_by = models.ForeignKey(USER_MODEL,
                                   default=None,
                                   on_delete=models.SET_DEFAULT,
                                   related_name="registrations_created",
                                   )
    created_on = models.DateTimeField(auto_now=True)
    applicants = models.ManyToManyField(USER_MODEL,
                                        default=None,
                                        related_name="applicant_for",
                                        )
    date_start = models.DateField(blank=True,
                                  null=True,
                                  )
    date_end = models.DateField(blank=True,
                                null=True,
                                )
