"""Application services for order workflows."""

from orders_app.models import Order


def create_order_from_detail(customer, detail):
    """Create an order snapshot from a selected offer tier."""
    return Order.objects.create(
        customer_user=customer,
        business_user=detail.offer.user,
        title=detail.title,
        revisions=detail.revisions,
        delivery_time_in_days=detail.delivery_time_in_days,
        price=detail.price,
        features=list(detail.features),
        offer_type=detail.offer_type,
    )
