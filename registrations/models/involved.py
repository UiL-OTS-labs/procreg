from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext as _

from . import Registration
from .registration import YES_NO, YES_NO_NA

# Create your models here.

USER_MODEL = get_user_model()


class Involved(models.Model):

    registration_related_name = "involved_groups"

    GROUP_TYPES = (
        ('consent', _("models:involved:consent")),
        ('non_consent', _("models:involved:non_consent")),
        ('guardian_consent', _("models:involved:guardian")),
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
        # SpecialDetail,
        on_delete=models.SET_DEFAULT,
    )
    gave_explicit_permission = models.CharField(
        max_length=10,
        choices=YES_NO,
    )
    explicit_permission_details = models.TextField(
        max_length=1000,
    )
    GROUNDS = (
        ("public", _("models:involved:public_grounds")),
        ("algemeen_belang", _("models:involved:algemeen_belang")),
        ("legal", _("models:involved:legal_grounds")),
    )
    grounds_for_exception = models.CharField(
        max_length=25,
        choices=GROUNDS,
    )
    algemeen_belang_details = models.TextField(
        max_length=1000,
    )
    legal_grounds_details = models.TextField(
        max_length=1000,
    )
    # Sensitive personal details
    provides_criminal_information = models.CharField(
        max_length=25,
        choices=YES_NO,
    )
    government_supervised_collection = models.CharField(
        max_length=25,
        choices=YES_NO,
    )
    involves_children_under_15 = models.CharField(
        max_length=25,
        choices=YES_NO,
    )
    confirm_parental_permission = models.CharField(
        max_length=25,
        choices=YES_NO,
    )
    other_sensitive_details = models.ManyToManyField(
        #SensitiveDetail,
        on_delete=models.SET_DEFAULT,
    )
    provides_no_sensitive_details = models.CharField(
        max_length=25,
        choices=YES_NO,
    )
    # Regular ol' details
    regular_details = models.ManyToManyField(
        #RegularDetail,
        on_delete=models.SET_DEFAULT,
    )
    social_media_details = models.ManyToManyField(
        #SocialMediaDetail,
        on_delete=models.CASCADE,
    )
    extra_details = models.ManyToManyField(
        #ExtraDetail,
        on_delete=models.CASCADE,
    )
    
        


class InformationKind(models.Model):
    description = models.CharField(
        max_length=200,
        default="",
    )
