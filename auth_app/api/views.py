"""Views for authentication endpoints."""

from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED
from rest_framework.views import APIView

from auth_app.api.serializers import LoginSerializer, RegistrationSerializer


def auth_payload(user):
    """Build the response shared by registration and login."""
    token, _ = Token.objects.get_or_create(user=user)
    return {
        "token": token.key,
        "username": user.username,
        "email": user.email,
        "user_id": user.pk,
    }


class RegistrationView(APIView):
    """Create customer and business accounts."""

    permission_classes = [AllowAny]

    def post(self, request):
        """Register a user and return an authentication token."""
        serializer = RegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(auth_payload(user), status=HTTP_201_CREATED)


class LoginView(APIView):
    """Authenticate existing Coderr users."""

    permission_classes = [AllowAny]

    def post(self, request):
        """Return an authentication token for valid credentials."""
        serializer = LoginSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        return Response(auth_payload(serializer.validated_data["user"]), HTTP_200_OK)
