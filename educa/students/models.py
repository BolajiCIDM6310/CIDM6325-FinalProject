from django.contrib.auth.models import User
from django.db import models
from courses.fields import OrderField
from courses.models import Course
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.template.loader import render_to_string

from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
import os


class Portfolio(models.Model):
    course = models.ForeignKey(Course, related_name="stud_modules", on_delete=models.CASCADE)
    student = models.ForeignKey(
        User,
        related_name='portfolio_created',
        on_delete=models.CASCADE
    )
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    overview = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created"]

    def __str__(self):
        return self.title


class PortContent(models.Model):
    portfolio = models.ForeignKey(
        Portfolio, related_name="port_contents", on_delete=models.CASCADE
    )
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        limit_choices_to={"model__in": ("text", "video", "image", "file")},
    )
    object_id = models.PositiveIntegerField()
    item = GenericForeignKey("content_type", "object_id")
    order = OrderField(blank=True, for_fields=["portfolio"])

    class Meta:
        ordering = ["order"]


# abstract class for other classes' use
class ItemBasePort(models.Model):
    student = models.ForeignKey(
        User, related_name="%(class)s_related_port", on_delete=models.CASCADE
    )
    title = models.CharField(max_length=250)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.title

    def render(self):
        return render_to_string(
            f'students/content/{self._meta.model_name}.html',
            {'item': self}
        )


class Text(ItemBasePort):
    content = models.TextField()


class File(ItemBasePort):
    file = models.FileField(
        upload_to="files",
        validators=[FileExtensionValidator(allowed_extensions=["pdf"])],
    )

    def clean(self):
        if not self.file.name.endswith(".pdf"):
            raise ValidationError("Only PDF files are allowed.")
        super().clean()


class Image(ItemBasePort):
    file = models.FileField(
        upload_to="images",
        validators=[FileExtensionValidator(allowed_extensions=["png"])],
    )

    def clean(self):
        if not self.file.name.endswith(".png"):
            raise ValidationError("Only PNG images are allowed.")
        super().clean()


class Video(ItemBasePort):
    url = models.URLField(blank=True, null=True)
    file = models.FileField(
        upload_to="videos",
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=["mp4"])],
    )

    def clean(self):
        if self.file and not self.file.name.endswith(".mp4"):
            raise ValidationError("Only MP4 videos are allowed.")
        if not (self.url or self.file):
            raise ValidationError("Provide either a video URL or an uploaded MP4 file.")
        super().clean()
