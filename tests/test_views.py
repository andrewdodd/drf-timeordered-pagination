import pytest
from mock import Mock, sentinel, patch
from datetime import datetime

from django.utils import timezone


from rest_framework.settings import api_settings
from rest_framework.test import APIRequestFactory

from timeordered_pagination.views import TimeOrderedPaginationViewSetMixin

from tests.models import (ModelWithModified, ModelWithAnotherField)
from tests.views import (ViewSetWithModified, ViewSetWithAnotherField)


factory = APIRequestFactory()


class IsTimeOrderedPaginationRequestTests:

    def test_request_is_for_timeordered_pagination_if_it_has_the_after_param(
            self):
        sut = TimeOrderedPaginationViewSetMixin()
        sut.request = Mock()
        sut.request.query_params = {'modified_after': 'anything'}
        assert sut.is_timeordered_pagination_request()

    def test_request_is_for_timeordered_pagination_if_it_has_the_from_param(
            self):
        sut = TimeOrderedPaginationViewSetMixin()
        sut.request = Mock()
        sut.request.query_params = {'modified_from': 'anything'}
        assert sut.is_timeordered_pagination_request()

    def test_it_uses_customised_after_param(self):
        class ViewSet(TimeOrderedPaginationViewSetMixin):
            modified_after_query_param = 'magical_new_param_value'

        sut = ViewSet()
        sut.request = Mock()
        sut.request.query_params = {'modified_after': 'anything'}
        assert not sut.is_timeordered_pagination_request()

        sut.request.query_params = {'magical_new_param_value': 'anything'}
        assert sut.is_timeordered_pagination_request()

    def test_it_uses_customised_from_param(self):
        class ViewSet(TimeOrderedPaginationViewSetMixin):
            modified_from_query_param = 'magical_new_param_value'

        sut = ViewSet()
        sut.request = Mock()
        sut.request.query_params = {'modified_from': 'anything'}
        assert not sut.is_timeordered_pagination_request()

        sut.request.query_params = {'magical_new_param_value': 'anything'}
        assert sut.is_timeordered_pagination_request()


class SuperViewSet:
    super_paginator = sentinel.super_paginator

    @property
    def paginator(self):
        return self.super_paginator


class ViewSet(TimeOrderedPaginationViewSetMixin, SuperViewSet):
    pass


class ItReturnsCustomPaginatorTests:

    def test_it_returns_normal_paginator_if_not_for_timeordered_pagination(
            self):
        sut = ViewSet()
        with patch.object(sut, 'is_timeordered_pagination_request') as\
                is_time_ordered:
            is_time_ordered.return_value = False
            assert sut.paginator == sentinel.super_paginator
            is_time_ordered.assert_called_once()

    @patch('timeordered_pagination.views.TimeOrderedPagination')
    def test_it_returns_custom_paginator_for_timeordered_pagination(
            self, CustomPagination):
        sut = TimeOrderedPaginationViewSetMixin()
        with patch.object(sut, 'is_timeordered_pagination_request') as\
                is_time_ordered:
            is_time_ordered.return_value = True
            assert sut.paginator == CustomPagination.return_value
            is_time_ordered.assert_called_once()

    @patch('timeordered_pagination.views.TimeOrderedPagination')
    def test_it_returns_the_same_paginator_for_multiple_calls(
            self, CustomPagination):
        sut = TimeOrderedPaginationViewSetMixin()
        with patch.object(sut, 'is_timeordered_pagination_request') as\
                is_time_ordered:
            is_time_ordered.return_value = True
            assert sut.paginator == CustomPagination.return_value
            assert sut.paginator == CustomPagination.return_value
            CustomPagination.assert_called_once()

    @patch('timeordered_pagination.views.TimeOrderedPagination')
    def test_it_builds_the_correct_paginator(self, CustomPagination):
        sut = TimeOrderedPaginationViewSetMixin()
        sut.target_field = 'custom_time_field'
        sut.start_from_target_field = 'custom_db_id_field'
        sut.limit_query_param_override = 'custom_limit_param'
        sut.max_limit_override = 'custom_max_limit_param'

        with patch.object(sut, 'is_timeordered_pagination_request') as\
                is_time_ordered:
            is_time_ordered.return_value = True
            assert sut.paginator == CustomPagination.return_value
            CustomPagination.assert_called_once_with(
                'custom_time_field',
                'custom_time_field_after',
                'custom_time_field_from',
                'custom_db_id_field',
                'start_from_custom_db_id_field',
                sut.limit_query_param_override,
                sut.max_limit_override)


@pytest.mark.django_db
class TestQueryset:

    def setup(self):
        self.models = [
            ModelWithModified.objects.create(n=1),
            ModelWithModified.objects.create(n=2),
            ModelWithModified.objects.create(n=3),
            ModelWithModified.objects.create(n=4),
            ModelWithModified.objects.create(n=5),
            ModelWithModified.objects.create(n=6),
        ]

        self.view = ViewSetWithModified.as_view({'get': 'list'})

    def test_it_returns_normal_queryset(self):
        default_page_size = api_settings.PAGE_SIZE
        request = factory.get('/data/')
        response = self.view(request)
        assert response.data['results'] == list(
            ModelWithModified.objects.all()[:default_page_size])

    def test_it_uses_default_page_size_for_timeordered_query(self):
        default_page_size = api_settings.PAGE_SIZE
        request = factory.get(
            '/data/', {'modified_from': self.models[0].modified.isoformat()})
        response = self.view(request)
        assert response.data['results'] == list(
            ModelWithModified.objects.all()[:default_page_size])

    def test_it_allows_limit_to_be_set_in_query_param(self):
        request = factory.get('/data/', {
            'modified_from': self.models[0].modified.isoformat(),
            'limit': 2,
        })
        response = self.view(request)
        assert response.data['results'] == list(
            ModelWithModified.objects.all()[:2])

    def test_it_includes_matching_times_for_the_from_query_param(self):
        request = factory.get('/data/', {
            'modified_from': self.models[-1].modified.isoformat(),
        })

        response = self.view(request)
        assert response.data['results'] == [ModelWithModified.objects.last()]

    def test_it_omits_matching_times_for_the_after_query_param(self):
        request = factory.get('/data/', {
            'modified_after': self.models[-1].modified.isoformat(),
        })

        response = self.view(request)
        assert response.data['results'] == []

    def test_it_obeys_after_query_param_if_both_after_and_from_are_included(
            self):
        request = factory.get('/data/', {
            'modified_after': self.models[-1].modified.isoformat(),
            'modified_from': self.models[-1].modified.isoformat(),
        })

        response = self.view(request)
        assert response.data['results'] == []


@pytest.mark.django_db
class TestQuerysetLogic:

    def setup(self):
        self.start_of_test = timezone.now()
        self.view = ViewSetWithModified.as_view({'get': 'list'})

        # default ordering is by 'n' field
        self.first = ModelWithModified.objects.create(n=2)
        self.middle_firstPK = ModelWithModified.objects.create(n=4)
        self.middle_secondPK = ModelWithModified.objects.create(
            n=1,
            modified=self.middle_firstPK.modified
        )
        self.last = ModelWithModified.objects.create(n=3)

    def test_normal_queryset_obeys_default_ordering(self):
        request = factory.get('/data/')
        response = self.view(request)
        # default ordering is by 'n' field
        assert response.data['results'] == [
            self.middle_secondPK,
            self.first,
            self.last,
            self.middle_firstPK]

    def test_it_returns_in_custom_order_by_for_from_query_param(
            self):
        request = factory.get('/data/', {'modified_from': self.start_of_test})
        response = self.view(request)
        assert response.data['results'] == [
            self.first,
            self.middle_firstPK,
            self.middle_secondPK,
            self.last]

    def test_it_returns_in_custom_order_by_for_after_query_param(
            self):
        request = factory.get('/data/', {'modified_after': self.start_of_test})
        response = self.view(request)
        assert response.data['results'] == [
            self.first,
            self.middle_firstPK,
            self.middle_secondPK,
            self.last]

    def test_it_returns_from_specified_time(self):
        request = factory.get('/data/', {
            'modified_from': self.middle_firstPK.modified.isoformat(),
        })
        response = self.view(request)
        assert response.data['results'] == [
            self.middle_firstPK,
            self.middle_secondPK,
            self.last]

    def test_it_returns_from_specified_time_and_immutable_db_field(self):
        request = factory.get('/data/', {
            'modified_from': self.middle_firstPK.modified.isoformat(),
            'start_from_id': self.middle_secondPK.id,
        })
        response = self.view(request)
        assert response.data['results'] == [
            self.middle_secondPK,
            self.last]

    def test_it_returns_correct_results_if_elements_have_updated_before_call(
            self):
        request = factory.get('/data/', {
            'modified_from': self.middle_firstPK.modified.isoformat(),
            'start_from_id': self.middle_firstPK.id,
        })
        response = self.view(request)
        # pre assertion
        assert response.data['results'] == [
            self.middle_firstPK,
            self.middle_secondPK,
            self.last]

        # check if only 1 has updated
        self.middle_firstPK.save()
        response = self.view(request)
        assert response.data['results'] == [
            self.middle_secondPK,
            self.last,
            self.middle_firstPK]

        # check if 2 have updated
        self.middle_secondPK.save()
        response = self.view(request)
        assert response.data['results'] == [
            self.last,
            self.middle_firstPK,
            self.middle_secondPK]


@pytest.mark.django_db
class TestWithAnotherField:

    def setup(self):
        self.start_of_test = timezone.now()
        self.view = ViewSetWithAnotherField.as_view({'get': 'list'})

        # default ordering is by 'n' field
        self.first = ModelWithAnotherField.objects.create(n=2, another_field=datetime(2000, 1, 1))
        self.middle_of_test = datetime(2000, 1, 2)
        self.middle_firstPK = ModelWithAnotherField.objects.create(n=4, another_field=datetime(2000, 1, 3))
        self.middle_secondPK = ModelWithAnotherField.objects.create(
            n=1, another_field=self.middle_firstPK.another_field
        )
        self.last = ModelWithAnotherField.objects.create(n=3, another_field=datetime(2000, 1, 4))

    def test_normal_queryset_obeys_default_ordering(self):
        request = factory.get('/data-with-another-field/')
        response = self.view(request)
        # default ordering is by 'n' field
        assert response.data['results'] == [
            self.middle_secondPK,
            self.first,
            self.last,
            self.middle_firstPK]

    def test_it_returns_in_custom_order_by_for_from_query_param(
            self):
        request = factory.get('/data-with-another-field/',
                              {'another_field_from': self.middle_of_test})
        response = self.view(request)
        assert response.data['results'] == [
            self.middle_firstPK,
            self.middle_secondPK,
            self.last]

    def test_it_returns_in_custom_order_by_for_after_query_param(
            self):
        request = factory.get('/data-with-another-field/',
                              {'another_field_after': self.middle_of_test})
        response = self.view(request)
        assert response.data['results'] == [
            self.middle_firstPK,
            self.middle_secondPK,
            self.last]

    def test_it_returns_from_specified_time_and_immutable_db_field(self):
        request = factory.get('/data-with-another-field/', {
            'another_field_from':
                self.middle_firstPK.another_field.isoformat(),
            'start_from_id': self.middle_secondPK.id,
        })
        response = self.view(request)
        assert response.data['results'] == [
            self.middle_secondPK,
            self.last]
