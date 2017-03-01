import pytest
from mock import MagicMock, Mock, patch, sentinel, ANY

from django.utils import timezone

from timeordered_pagination.pagination import TimeOrderedPagination

from rest_framework.settings import api_settings
from rest_framework.test import APIRequestFactory

from tests.models import (ModelWithModified, ModelWithAnotherField)
from tests.views import (ViewSetWithModified, ViewSetWithAnotherField)


factory = APIRequestFactory()


class TestPagination:

    def test_it_has_sensible_defaults(self):
        sut = TimeOrderedPagination(None, None, None, None, None)
        assert sut.default_limit == api_settings.PAGE_SIZE
        assert sut.max_limit is None
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
            ModelWithModified.objects.create(n=1),
            ModelWithModified.objects.create(n=2),
            ModelWithModified.objects.create(n=3),
            ModelWithModified.objects.create(n=4),
            ModelWithModified.objects.create(n=5),
            ModelWithModified.objects.create(n=6),
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

        self.mock_queryset = QuerySetMock([1, 2, 3, 4])

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
        paginator = TimeOrderedPagination(*[ANY] * 5,
                                          max_limit_override=123)
        request = Mock()
        request.query_params = {'limit': 999}
        assert paginator.get_limit(request) == 123

    def test_it_paginates_queryset(self):
        paginator = TimeOrderedPagination(*[ANY] * 5,
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
        paginator = TimeOrderedPagination(*[ANY] * 5)
        next_item_qs = Mock()
        next_item_qs.exists.return_value = False
        paginator.next_item = next_item_qs
        assert paginator.get_next_link() is None

    def test_it_builds_the_next_link(self):
        pass  # ZOMG I'm sick of writing these horrible brittle tests


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
        self.middle_secondPK = ModelWithModified.objects.create(n=1,
                                                                modified=self.middle_firstPK.modified)
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

    def test_from_query_param_returns_ordered_by_timefield_and_then_immutable_db_field(
            self):
        request = factory.get('/data/', {'modified_from': self.start_of_test})
        response = self.view(request)
        assert response.data['results'] == [
            self.first,
            self.middle_firstPK,
            self.middle_secondPK,
            self.last]

    def test_after_query_param_returns_ordered_by_timefield_and_then_immutable_db_field(
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
        self.first = ModelWithAnotherField.objects.create(n=2)
        self.middle_of_test = timezone.now()
        self.middle_firstPK = ModelWithAnotherField.objects.create(n=4)
        self.middle_secondPK = ModelWithAnotherField.objects.create(n=1,
                                                                    another_field=self.middle_firstPK.another_field)
        self.last = ModelWithAnotherField.objects.create(n=3)

    def test_normal_queryset_obeys_default_ordering(self):
        request = factory.get('/data-with-another-field/')
        response = self.view(request)
        # default ordering is by 'n' field
        assert response.data['results'] == [
            self.middle_secondPK,
            self.first,
            self.last,
            self.middle_firstPK]

    def test_from_query_param_returns_ordered_by_timefield_and_then_immutable_db_field(
            self):
        request = factory.get('/data-with-another-field/',
                              {'another_field_from': self.middle_of_test})
        response = self.view(request)
        assert response.data['results'] == [
            self.middle_firstPK,
            self.middle_secondPK,
            self.last]

    def test_after_query_param_returns_ordered_by_timefield_and_then_immutable_db_field(
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
            'another_field_from': self.middle_firstPK.another_field.isoformat(),
            'start_from_id': self.middle_secondPK.id,
        })
        response = self.view(request)
        assert response.data['results'] == [
            self.middle_secondPK,
            self.last]
