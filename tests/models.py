from django.db import models
from model_utils.models import TimeStampedModel


class TestModel(TimeStampedModel):
    n = models.IntegerField("An integer")

    class Meta:
        ordering = ('n',)
