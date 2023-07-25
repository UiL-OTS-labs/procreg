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
    slug = models.CharField(
        max_length=100,
        default="",
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
    question_slugs = models.TextField(
        verbose_name="Line-separated list of related question slugs",
        default=""
    )
