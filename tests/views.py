from rest_framework import serializers
from rest_framework.viewsets import ReadOnlyModelViewSet
from timeordered_pagination.views import TimeOrderedPaginationViewSetMixin

from tests.models import ModelWithModified, ModelWithAnotherField


class PassThroughSerializer(serializers.BaseSerializer):

    def to_representation(self, item):
        return item


class ViewSetWithModified(TimeOrderedPaginationViewSetMixin,
                          ReadOnlyModelViewSet):
    queryset = ModelWithModified.objects.all()
    serializer_class = PassThroughSerializer
    ordering = 'id'


class ViewSetWithAnotherField(TimeOrderedPaginationViewSetMixin,
                              ReadOnlyModelViewSet):
    queryset = ModelWithAnotherField.objects.all()
    serializer_class = PassThroughSerializer
    ordering = 'id'
    target_field = 'another_field'
