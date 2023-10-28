import os
import uuid

from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext as _


def create_custom_image_file_path(instance, filename):
    _, extension = os.path.splitext(filename)
    filename = f"{slugify(instance.title)}-{uuid.uuid4()}{extension}"

    return os.path.join("uploads", "books", filename)


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
    image = models.ImageField(
        null=True,
        blank=True,
        upload_to=create_custom_image_file_path,
    )

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title
