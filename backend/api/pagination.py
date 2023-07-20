from rest_framework.pagination import PageNumberPagination


class SubscribePagination(PageNumberPagination):
    page_size_query_param = "limit"
