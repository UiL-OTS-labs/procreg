from django.db import models

class InformationKind(models.Model):
    """
    Abstract base class to base kinds of information on.
    """

    preferred_relationship = models.CASCADE

    name = models.CharField(
        max_length=200,
        default="",
    )

    class Meta:
        abstract = True


class SpecialDetail(InformationKind):
    pass

class SensitiveDetail(InformationKind):
    pass

class RegularDetail(InformationKind):
    pass

class SocialMediaDetail(InformationKind):
    pass

class ICFormDetail(InformationKind):
    pass

class ExtraDetail(InformationKind):
    pass
