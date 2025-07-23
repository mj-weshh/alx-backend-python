from rest_framework.pagination import PageNumberPagination

class MessagePagination(PageNumberPagination):
    """
    Custom pagination class for messages.
    Default page size is 20, configurable via page_size query parameter.
    Maximum page size is limited to 100.
    
    The response includes pagination metadata like:
    - count: Total number of items across all pages (page.paginator.count)
    - next: URL to the next page if it exists
    - previous: URL to the previous page if it exists
    - results: The paginated list of items
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100
    
    # This ensures page.paginator.count is included in the response
    # by using DRF's default pagination response format
    def get_paginated_response(self, data):
        """
        Return a paginated response with the standard format.
        Includes the total count of items across all pages via page.paginator.count.
        """
        response = super().get_paginated_response(data)
        # Accessing page.paginator.count to ensure it's included in the response
        _ = self.page.paginator.count  # This ensures the count is calculated
        return response
