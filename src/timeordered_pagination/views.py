from django.db.models import Q

from .pagination import TimeOrderedPagination

import logging
logger = logging.getLogger(__name__)


class TimeOrderedPaginationViewSetMixin(object):
    """
    Filters the list of items based on their modified time

    This is achieved by allowing two different query parameters:
     - 'modified_after' -> which translates into a 'X > modified' filter
     - 'modified_from' -> which translates into a 'X >= modified' filter

    Both of these are usable by themselves. If both are supplied then
    'modified_after' will prevail.

    Two other query paramters are supported:
     - 'limit' -> which will set the maximum number of items included in a
            single page. NB: This will be capped at the class's configured
            'max_limit' value.
     - 'start_from_<TARGET FIELD>' -> which will be used in conjunction with
            'modified_from' to choose which 'field' at which should be the
            first item in the page. This is necessary to allow robust
            pagination.
    """
    after_query_param_template = '{}_after'
    from_query_param_template = '{}_from'
    start_from_query_param_template = 'start_from_{}'
    target_field = 'modified'
    start_from_target_field = 'id'
    limit_query_param_override = None
    max_limit_override = None

    @property
    def start_from_query_param(self):
        return self.start_from_query_param_template.format(
            self.start_from_target_field)

    @property
    def modified_after_query_param(self):
        return self.after_query_param_template.format(self.target_field)

    @property
    def modified_from_query_param(self):
        return self.from_query_param_template.format(self.target_field)

    def get_queryset(self):
        queryset = super(TimeOrderedPaginationViewSetMixin,
                         self).get_queryset()

        if not self.is_timeordered_pagination_request():
            # Nothing for us to do
            return queryset

        query_params = self.request.query_params
        modified_after = query_params.get(
            self.modified_after_query_param, None)
        modified_from = query_params.get(self.modified_from_query_param, None)

        if modified_after is not None:
            queryset = queryset.filter(**{
                self.target_field + '__gt': modified_after
            })
        elif modified_from is not None:
            start_at = query_params.get(self.start_from_query_param, None)
            if start_at is None:
                queryset = queryset.filter(**{
                    self.target_field + '__gte': modified_from
                })
            else:
                # modified > modified_from || modified == modified_from and id
                # >= start_at
                query = Q(**{self.target_field + '__gt': modified_from}) |\
                    (Q(**{self.target_field: modified_from}) &
                     Q(**{self.start_from_target_field + '__gte': start_at}))
                queryset = queryset.filter(query)
        else:
            logger.error('This should not be possible')

        # Ensure order by modified then 'id', as this is how we maintain a
        # consistent ordering between calls
        queryset = queryset.order_by(
            self.target_field, self.start_from_target_field)

        return queryset

    def is_timeordered_pagination_request(self):
        modified_after = self.request.query_params.get(
            self.modified_after_query_param, None)
        modified_from = self.request.query_params.get(
            self.modified_from_query_param, None)
        return modified_after is not None or modified_from is not None

    @property
    def paginator(self):
        if self.is_timeordered_pagination_request():
            if not hasattr(self, '_timeordered_paginator'):
                self._timeordered_paginator = TimeOrderedPagination(
                    self.target_field,
                    self.modified_after_query_param,
                    self.modified_from_query_param,
                    self.start_from_target_field,
                    self.start_from_query_param,
                    self.limit_query_param_override,
                    self.max_limit_override)

            return self._timeordered_paginator
        return super(TimeOrderedPaginationViewSetMixin, self).paginator
