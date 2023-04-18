from django.db import models
from django.utils.translation import gettext_lazy as _


class Faq(models.Model):

    title = models.CharField(
        max_length=500,
        default="",
    )
    answer = models.TextField(
        max_length=5000,
        default="",
        blank=True,
    )
    front_page = models.BooleanField(
        default=False,
    )
    external_url = models.CharField(
        max_length=500,
        default="",
        blank=True,
    )
    external_url_text = models.CharField(
        max_length=500,
        default="",
        blank=True,
    )
