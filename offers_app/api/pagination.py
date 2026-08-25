"""Pagination classes for offers."""

from rest_framework.pagination import PageNumberPagination


class OfferPagination(PageNumberPagination):
    """Allow the frontend to choose a bounded page size."""

    page_size = 6
    page_size_query_param = "page_size"
    max_page_size = 100
