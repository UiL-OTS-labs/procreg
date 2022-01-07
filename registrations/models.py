from django.db import models

# Create your models here.


class Registration(models.Model):

    title = models.CharField(max_length=200,
                             help_text="models:registration_title_help_text",
    )
