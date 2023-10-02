from django.conf import settings
from rest_framework import pagination
from rest_framework.response import Response


class PageWithTotalPage(pagination.PageNumberPagination):
    page_size_query_param = 'page_size'
    def get_paginated_response(self, data):


        return Response({
            'links': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count': self.page.paginator.count,
            'results': data
        })
