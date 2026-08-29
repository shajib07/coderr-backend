"""Cross-domain aggregation services."""

from django.db.models import Avg, Count

from auth_app.models import User
from offers_app.models import Offer
from profile_app.models import Profile
from reviews_app.models import Review


def get_review_summary():
    """Return the total review count and raw average rating."""
    return Review.objects.aggregate(
        review_count=Count("id"),
        average_rating=Avg("rating"),
    )


def get_base_info():
    """Return the documented public platform statistics."""
    review_data = get_review_summary()
    average_rating = round(float(review_data["average_rating"] or 0), 1)
    business_profiles = Profile.objects.filter(
        user__type=User.UserType.BUSINESS
    ).count()
    return {
        "review_count": review_data["review_count"],
        "average_rating": average_rating,
        "business_profile_count": business_profiles,
        "offer_count": Offer.objects.count(),
    }
