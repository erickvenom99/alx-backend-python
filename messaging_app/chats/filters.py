import django_filters
from django_filters import DateFromToRangeFilter
from .models import Message, User
 # <-- Import Response

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
