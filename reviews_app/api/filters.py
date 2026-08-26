"""Filtering helpers for reviews."""

from rest_framework.exceptions import ValidationError
from rest_framework.filters import BaseFilterBackend


def optional_integer(params, name):
    """Parse an optional integer filter value."""
    value = params.get(name)
    if value is None:
        return None
    try:
        return int(value)
    except ValueError as error:
        raise ValidationError({name: "Enter a valid integer."}) from error


class ReviewFilterBackend(BaseFilterBackend):
    """Filter reviews by their business user or reviewer."""

    def filter_queryset(self, request, queryset, view):
        business_id = optional_integer(request.query_params, "business_user_id")
        reviewer_id = optional_integer(request.query_params, "reviewer_id")
        if business_id is not None:
            queryset = queryset.filter(business_user_id=business_id)
        if reviewer_id is not None:
            queryset = queryset.filter(reviewer_id=reviewer_id)
        return queryset
