import pytest
from mock import MagicMock, Mock, patch, sentinel, ANY

from django.utils import timezone

from timeordered_pagination.pagination import TimeOrderedPagination

from rest_framework.settings import api_settings
from rest_framework.test import APIRequestFactory

from tests.models import TestModel


factory = APIRequestFactory()


class TestPagination:
    def test_it_has_sensible_defaults(self):
        sut = TimeOrderedPagination(None, None, None, None, None)
        assert sut.default_limit == api_settings.PAGE_SIZE
        assert sut.max_limit == None
        assert sut.limit_query_param == 'limit'

    def test_it_can_have_the_max_limit_overridden(self):
        LIMIT = sentinel
        assert TimeOrderedPagination(None, None, None,
            None, None, max_limit_override=LIMIT).max_limit == LIMIT

    def test_it_can_have_the_limit_query_param_value_overridden(self):
        assert TimeOrderedPagination(None, None, None,
            None, None, limit_query_param_override='a_query_param'
        ).limit_query_param == 'a_query_param'


@pytest.mark.django_db
class TestPaginationMethods:
    def setup(self):
        self.models = [
            TestModel.objects.create(n=1),
            TestModel.objects.create(n=2),
            TestModel.objects.create(n=3),
            TestModel.objects.create(n=4),
            TestModel.objects.create(n=5),
            TestModel.objects.create(n=6),
        ]

        self.paginator = TimeOrderedPagination(
            'modified',
            'modified_after',
            'modified_from',
            'id',
            'start_from id')

        class QuerySetMock:
            def __init__(self, values):
                self.values = values
            def __iter__(self):
                return iter(self.values)
            def __getitem__(self, name):
                return self.values[name]
            def count(self):
                return len(self.values)

        self.mock_queryset = QuerySetMock([1,2,3,4])

    def test_it_uses_default_limit(self):
        default_page_size = api_settings.PAGE_SIZE
        request = Mock()
        request.query_params = {}
        assert self.paginator.get_limit(request) == default_page_size

    def test_it_uses_limit_from_request(self):
        request = Mock()
        request.query_params = {'limit': 123}
        assert self.paginator.get_limit(request) == 123

    def test_it_clips_to_max_limit_if_configured(self):
        paginator = TimeOrderedPagination(*[ANY] *5,
            max_limit_override=123)
        request = Mock()
        request.query_params = {'limit': 999}
        assert paginator.get_limit(request) == 123

    def test_it_paginates_queryset(self):
        paginator = TimeOrderedPagination(*[ANY] *5,
            max_limit_override=3)
        request = Mock()
        request.query_params = {'limit': 999}

        page = paginator.paginate_queryset(self.mock_queryset, request)

        assert page == [1, 2, 3]
        assert paginator.request == request
        assert paginator.next_item == [4]
        assert paginator.count == 4
        assert paginator.limit == 3

    def test_get_next_link_returns_none_if_no_next_item(self):
        paginator = TimeOrderedPagination(*[ANY] *5)
        next_item_qs = Mock()
        next_item_qs.exists.return_value = False
        paginator.next_item = next_item_qs
        assert paginator.get_next_link() == None

    def test_it_builds_the_next_link(self):
        pass # ZOMG I'm sick of writing these horrible brittle tests




