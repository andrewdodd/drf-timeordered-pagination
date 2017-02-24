from rest_framework import serializers
from rest_framework.viewsets import ReadOnlyModelViewSet
from timeordered_pagination.views import TimeOrderedPaginationViewSetMixin

from tests.models import TestModel


class TestSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestModel
        fields = ('id', 'n')


class PassThroughSerializer(serializers.BaseSerializer):
    def to_representation(self, item):
        return item


class TestViewSet(TimeOrderedPaginationViewSetMixin, ReadOnlyModelViewSet):
    queryset = TestModel.objects.all()
    serializer_class = PassThroughSerializer
    ordering = 'id'
