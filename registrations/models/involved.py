from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext as _

from . import Registration
from .details import SpecialDetail, SensitiveDetail, SocialMediaDetail, \
    ExtraDetail, RegularDetail, ICFormDetail
from .registration import YES_NO, YES_NO_NA

# Create your models here.

USER_MODEL = get_user_model()


class Involved(models.Model):

    registration_related_name = "involved_groups"

    GROUP_TYPES = (
        ('knowingly', _("models:involved:knowingly")),
        ('not_knowingly', _("models:involved:not_knowingly")),
        ('guardian', _("models:involved:guardian")),
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
    # Fields relating to personal information
    special_details = models.ManyToManyField(
        to=SpecialDetail,
    )
    gave_explicit_permission = models.BooleanField(
        null=True,
        default=None,
    )
    explicit_permission_details = models.TextField(
        max_length=1000,
        default="",
    )
    GROUNDS = (
        ("public", _("models:involved:public_grounds")),
        ("algemeen_belang", _("models:involved:algemeen_belang")),
        ("legal", _("models:involved:legal_grounds")),
    )
    grounds_for_exception = models.CharField(
        max_length=25,
        choices=GROUNDS,
        default="",
    )
    algemeen_belang_details = models.TextField(
        max_length=1000,
        default="",
    )
    legal_grounds_details = models.TextField(
        max_length=1000,
        default="",
    )
    # Sensitive personal details
    provides_criminal_information = models.BooleanField(
        null=True,
        default=None,
    )
    government_supervised_collection = models.BooleanField(
        null=True,
        default=None,
    )
    involves_children_under_15 = models.BooleanField(
        null=True,
        default=None,
    )
    confirm_parental_permission = models.BooleanField(
        null=True,
        default=None,
    )
    other_sensitive_details = models.ManyToManyField(
        SensitiveDetail
    )
    provides_no_sensitive_details = models.BooleanField(
        null=True,
        default=None,
    )
    # Regular ol' details
    regular_details = models.ManyToManyField(
        RegularDetail,
    )
    social_media_details = models.ManyToManyField(
        SocialMediaDetail,
    )
    extra_details = models.ManyToManyField(
        ExtraDetail,
    )
    provides_ic_form = models.BooleanField(
        null=True,
        default=None,
    )
    ic_form_details = models.ManyToManyField(
        ICFormDetail,
    )
