"""Filtering helpers for the public offer list."""

from decimal import Decimal, InvalidOperation

from rest_framework.exceptions import ValidationError
from rest_framework.filters import BaseFilterBackend


def decimal_parameter(params, name):
    """Parse an optional decimal query parameter."""
    value = params.get(name)
    if value is None:
        return None
    try:
        return Decimal(value)
    except InvalidOperation as error:
        raise ValidationError({name: "Enter a valid number."}) from error


def integer_parameter(params, name):
    """Parse an optional integer query parameter."""
    value = params.get(name)
    if value is None:
        return None
    try:
        return int(value)
    except ValueError as error:
        raise ValidationError({name: "Enter a valid integer."}) from error


class OfferFilterBackend(BaseFilterBackend):
    """Apply the documented creator, price, and delivery filters."""

    def filter_queryset(self, request, queryset, view):
        params = request.query_params
        creator_id = integer_parameter(params, "creator_id")
        min_price = decimal_parameter(params, "min_price")
        max_delivery = integer_parameter(params, "max_delivery_time")
        if creator_id is not None:
            queryset = queryset.filter(user_id=creator_id)
        if min_price is not None:
            queryset = queryset.filter(min_price__gte=min_price)
        if max_delivery is not None:
            queryset = queryset.filter(min_delivery_time__lte=max_delivery)
        return queryset
