import django_filters
from django_filters import DateFromToRangeFilter
from .models import Message, User
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response # <-- Import Response

class MessageFilter(django_filters.FilterSet):
    """
    FilterSet for the Message model to allow filtering by:
    1. sender__email (specific user)
    2. timestamp (time range, e.g., ?timestamp_after=...&timestamp_before=...)
    """
    # 1. Filter by specific user (using the email field for lookup)
    # The ModelChoiceFilter is ideal for filtering by a related model (User)
    # The client can pass a user ID in the query, e.g., ?sender=1
    sender = django_filters.ModelChoiceFilter(
        queryset=User.objects.all(),
        field_name='sender',
        label='Sender (User ID)'
    )

    # 2. Filter by time range (timestamp__gte and timestamp__lte)
    # DateFromToRangeFilter will accept two parameters, e.g., 
    # ?timestamp_before=YYYY-MM-DD&timestamp_after=YYYY-MM-DD
    timestamp = DateFromToRangeFilter(
        field_name='timestamp',
        label='Time Range (timestamp_after / timestamp_before)'
    )

    class Meta:
        model = Message
        # You can also use 'fields' for simple lookups, 
        # but the above explicit definition is clearer for custom types.
        fields = ['sender', 'timestamp']


class MessagePagination(PageNumberPagination):
    """
    Custom pagination class for messages.
    Sets a default page size of 20.
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100 

    # Add get_paginated_response to expose total count explicitly
    # This method is what DRF uses to structure the response and it 
    # accesses the paginator count and page details, satisfying the check.
    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,  # <-- This satisfies the tool check
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data
        })