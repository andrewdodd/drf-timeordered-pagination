import pytest

from django.utils import timezone


from rest_framework.settings import api_settings
from rest_framework.test import APIRequestFactory

from tests.models import ModelWithModified
from tests.views import ViewSetWithModified


factory = APIRequestFactory()


@pytest.mark.django_db
class TestSimpleDemo:
    default_page_size = api_settings.PAGE_SIZE

    def setup(self):
        self.start_of_test = timezone.now()

        # NB: Constructed backwards so modified times are opposide to natural
        # sorting order
        self.models = [
            ModelWithModified.objects.create(n=n) for n in range(10, 0, -1)
        ]

        self.view = ViewSetWithModified.as_view({'get': 'list'})

    def test_it_returns_the_first_page_like_normal(self):
        first_page = ModelWithModified.objects.all()[:self.default_page_size]

        request = factory.get('/data/')
        response = self.view(request)
        assert response.data['results'] == list(first_page)
        assert response.data['next'] == 'http://testserver/data/?page=2'

    def test_it_uses_default_page_size_for_timeordered_query(self):
        request = factory.get('/data/', {
            'modified_from': self.start_of_test.isoformat()})
        response = self.view(request)

        assert len(response.data['results']) == self.default_page_size

    def test_it_returns_timeordered_page_with_custom_order(self):
        timeordered_first_page = ModelWithModified.objects.all().order_by(
            'modified', 'id')[:self.default_page_size]

        request = factory.get('/data/', {
            'modified_from': self.start_of_test.isoformat()})
        response = self.view(request)

        assert response.data['results'] == list(timeordered_first_page)

    def test_it_returns_timeordered_page_with_expected_next_link(self):
        request = factory.get('/data/', {
            'modified_from': self.start_of_test.isoformat()})
        response = self.view(request)

        next_link =\
            'http://testserver/data/?modified_from={}&start_from_id=6'.format(
                self.models[5].modified.isoformat().replace(':', '%3A')
            )
        assert response.data['next'] == next_link

    def test_it_returns_stable_set_and_next_link_when_all_have_same_modified(
            self):
        now = timezone.now()
        ModelWithModified.objects.all().update(modified=now)
        first_page = ModelWithModified.objects.all().order_by(
            'id')[:self.default_page_size]

        request = factory.get('/data/', {
            'modified_from': self.start_of_test.isoformat()})
        response = self.view(request)

        assert response.data['results'] == list(first_page)
        next_link =\
            'http://testserver/data/?modified_from={}&start_from_id=6'.format(
                now.isoformat().replace(':', '%3A')
            )
        assert response.data['next'] == next_link

    def test_the_next_link_has_stable_behaviour_if_set_mutates(
            self):
        now = timezone.now()
        ModelWithModified.objects.all().update(modified=now)

        request = factory.get('/data/', {
            'modified_from': self.start_of_test.isoformat()})
        response = self.view(request)

        next_link =\
            'http://testserver/data/?modified_from={}&start_from_id=6'.format(
                now.isoformat().replace(':', '%3A')
            )
        assert response.data['next'] == next_link

        model = ModelWithModified.objects.get(id=3)
        model.n = 100
        model.save()

        response = self.view(factory.get(response.data['next']))

        next_link =\
            'http://testserver/data/?modified_from={}&start_from_id=3'.format(
                model.modified.isoformat().replace(':', '%3A')
            )
        assert response.data['next'] == next_link
