from rest_framework import pagination
from rest_framework.response import Response
from rest_framework.utils.urls import replace_query_param, remove_query_param
from rest_framework.settings import api_settings


class TimeOrderedPagination(pagination.BasePagination):
    max_limit = None
    default_limit = api_settings.PAGE_SIZE
    limit_query_param = 'limit'

    def __init__(self,
                 target_field,
                 after_query_param,
                 from_query_param,
                 start_from_target_field,
                 start_from_id_query_param,
                 limit_query_param_override=None,
                 max_limit_override=None):
        self.target_field = target_field
        self.after_query_param = after_query_param
        self.from_query_param = from_query_param
        self.start_from_id_query_param = start_from_id_query_param
        self.start_from_target_field = start_from_target_field
        if limit_query_param_override:
            self.limit_query_param = limit_query_param_override
        if max_limit_override:
            self.max_limit = max_limit_override

    def get_next_link(self):
        if not self.next_item.exists():
            return None
        url = self.request.build_absolute_uri()
        next_item = self.next_item.get()
        after_value = getattr(next_item, self.target_field).isoformat()

        url = remove_query_param(url, self.after_query_param)
        url = replace_query_param(url, self.from_query_param, after_value)
        url = replace_query_param(url, self.start_from_id_query_param,
                                  getattr(next_item,
                                          self.start_from_target_field))
        return url

    def get_paginated_response(self, data):
        return Response({
            'next': self.get_next_link(),
            'previous': None,  # TODO - Should I include this?
            'count': self.count,
            'results': data,
        })

    def paginate_queryset(self, queryset, request, view=None):
        self.limit = self.get_limit(request)
        self.count = queryset.count()
        self.page = queryset[:self.limit]
        self.next_item = queryset[self.limit:(self.limit + 1)]
        self.request = request
        return self.page

    def get_limit(self, request):
        if self.limit_query_param:
            try:
                return pagination._positive_int(
                    request.query_params[self.limit_query_param],
                    strict=True,
                    cutoff=self.max_limit
                )
            except (KeyError, ValueError):
                pass
        return self.default_limit
