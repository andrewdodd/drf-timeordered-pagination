from django.conf.urls import url, include

from rest_framework import routers

from tests.views import TestViewSet, TestViewSetWithAnotherField


router = routers.DefaultRouter()
router.register(r'data', TestViewSet)
router.register(r'data-with-another-field', TestViewSetWithAnotherField)

urlpatterns = [
    url(r'^', include(router.urls)),
]
