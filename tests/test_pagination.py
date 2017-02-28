import pytest
from mock import Mock, patch, sentinel

from django.test import TestCase
from django.utils import timezone

from timeordered_pagination.views import TimeOrderedPaginationViewSetMixin

from rest_framework.test import APIRequestFactory
from rest_framework.settings import api_settings


factory = APIRequestFactory()


class IsTimeOrderedPaginationRequestTests(TestCase):
    def test_request_is_for_timeordered_pagination_if_it_has_the_after_param(self):
        sut = TimeOrderedPaginationViewSetMixin()
        sut.request = Mock()
        sut.request.query_params = {'modified_after': 'anything'}
        assert sut.is_timeordered_pagination_request()

    def test_request_is_for_timeordered_pagination_if_it_has_the_from_param(self):
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


class ItReturnsCustomPaginatorTests(TestCase):
    def test_it_returns_normal_paginator_if_request_not_for_timeordered_pagination(self):
        sut = ViewSet()
        with patch.object(sut, 'is_timeordered_pagination_request') as is_time_ordered:
            is_time_ordered.return_value = False
            assert sut.paginator == sentinel.super_paginator
            is_time_ordered.assert_called_once()

    @patch('timeordered_pagination.views.TimeOrderedPagination')
    def test_it_returns_custom_paginator_if_request_is_for_timeordered_pagination(
            self, CustomPagination):
        sut = TimeOrderedPaginationViewSetMixin()
        with patch.object(sut, 'is_timeordered_pagination_request') as is_time_ordered:
            is_time_ordered.return_value = True
            assert sut.paginator == CustomPagination.return_value
            is_time_ordered.assert_called_once()

    @patch('timeordered_pagination.views.TimeOrderedPagination')
    def test_it_returns_the_same_object_for_custom_pagination_for_multiple_calls(
            self, CustomPagination):
        sut = TimeOrderedPaginationViewSetMixin()
        with patch.object(sut, 'is_timeordered_pagination_request') as is_time_ordered:
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

        with patch.object(sut, 'is_timeordered_pagination_request') as is_time_ordered:
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

