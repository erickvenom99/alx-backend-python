from rest_framework.pagination import PageNumberPagination

class MessagePagination(PageNumberPagination):
    """
    Custom pagination class for messages.
    Sets a default page size of 20.
    """
    page_size = 20
    # Allows client to override the page size using a query parameter, 
    # if required, though the requirement suggests a fixed size. 
    # To strictly enforce 20, remove 'page_size_query_param'.
    page_size_query_param = 'page_size'
    max_page_size = 100 # Safety limit