from django.db import models
from django.utils.translation import gettext_lazy as _
from django.urls import reverse


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
        default=None,
        unique=True,
        null=True
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
        default="",
        blank=True,
    )

    @property
    def link(self):
        return reverse(
            "registrations:display_faq",
            kwargs={
                "pk": self.pk,
            }
        )

    def __str__(self):
        return self.slug


class FaqList(models.Model):

    slug = models.CharField(
        max_length=100,
        unique=True,
    )
    faqs = models.ManyToManyField(
        "registrations.Faq",
    )
    show_help_text = models.BooleanField(
        default=True,
    )
    help_text = models.TextField(
        default="",
    )

    def __str__(self):
        return self.slug
