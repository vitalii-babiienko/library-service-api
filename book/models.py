from django.db import models
from django.utils.translation import gettext as _


class Book(models.Model):
    class CoverType(models.TextChoices):
        HARD = "HARD", _("Hard")
        SOFT = "SOFT", _("Soft")

    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    cover = models.CharField(
        max_length=4,
        choices=CoverType.choices,
        default=CoverType.HARD,
    )
    inventory = models.PositiveIntegerField()
    daily_fee = models.DecimalField(
        max_digits=6,
        decimal_places=2,
    )

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title
