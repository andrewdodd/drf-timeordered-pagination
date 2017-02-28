from django.db import models
from model_utils.models import TimeStampedModel
from model_utils.fields import AutoLastModifiedField


class ModelWithModified(TimeStampedModel):
    n = models.IntegerField("An integer")

    class Meta:
        ordering = ('n',)


class ModelWithAnotherField(models.Model):
    n = models.IntegerField("An integer")
    another_field = AutoLastModifiedField()

    class Meta:
        ordering = ('n',)
