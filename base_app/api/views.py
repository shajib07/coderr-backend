"""Views for public base information."""

from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from base_app.api.serializers import BaseInfoSerializer
from base_app.services import get_base_info


class BaseInfoView(APIView):
    """Return public aggregate information about Coderr."""

    permission_classes = [AllowAny]

    def get(self, request):
        """Return current counts and the rounded average rating."""
        serializer = BaseInfoSerializer(get_base_info())
        return Response(serializer.data)

