import django_filters
from django.utils import timezone
from .models import Message

class MessageFilter(django_filters.FilterSet):
    """
    Filter for Message model.
    Allows filtering by:
    - sender: Filter messages by sender's email (case-insensitive)
    - start_time: Filter messages sent after this datetime
    - end_time: Filter messages sent before this datetime
    """
    user = django_filters.CharFilter(
        field_name='sender__email',
        lookup_expr='iexact',
        help_text='Filter by sender email (case-insensitive)'
    )
    start_time = django_filters.DateTimeFilter(
        field_name='sent_at',
        lookup_expr='gte',
        help_text='Filter messages sent after this datetime (format: YYYY-MM-DD HH:MM:SS)'
    )
    end_time = django_filters.DateTimeFilter(
        field_name='sent_at',
        lookup_expr='lte',
        help_text='Filter messages sent before this datetime (format: YYYY-MM-DD HH:MM:SS)'
    )

    class Meta:
        model = Message
        fields = {
            'sender__email': ['exact', 'iexact'],
            'sent_at': ['date', 'date__gte', 'date__lte', 'year', 'month', 'day'],
        }
