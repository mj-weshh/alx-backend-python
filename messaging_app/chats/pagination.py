from rest_framework.pagination import PageNumberPagination

class MessagePagination(PageNumberPagination):
    """
    Custom pagination class for messages.
    Default page size is 20, configurable via page_size query parameter.
    Maximum page size is limited to 100.
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100
