#Third party modules
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework import status
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.generics import ListCreateAPIView,ListAPIView

#Django modules
from django.contrib.auth import get_user_model

# Project modules
from apps.accounts.models import UserRole
from apps.accounts.api.v1.serializers import CustomerSerializer, LoginSerializer, PasswordResetConfirmSerializer, PasswordResetRequestSerializer, StaffSerializer

User = get_user_model()

# Login API view
class LoginView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "login"

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        tokens = serializer.save()

        return Response(tokens, status=status.HTTP_200_OK)

# Password Reset Request API view    
class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "password_reset"

    def post(self, request):

        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = serializer.save()

        return Response(result, status=status.HTTP_200_OK)

# Password Reset Confirm API view   
class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):

        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = serializer.save()

        return Response(result, status=status.HTTP_200_OK)
    
# Staff API view
class StaffView(ListCreateAPIView):
    serializer_class = StaffSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):

        user = self.request.user

        if user.role not in [UserRole.ADMIN, UserRole.MANAGER]:
            return User.objects.none()

        return User.objects.filter(
            tenant=user.tenant,
            role=UserRole.STAFF
        ).select_related("company")

    def get_serializer_context(self):
        return {"request": self.request}
    
# Customer API view
class CustomerListView(ListAPIView):
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):

        if self.request.user.role != UserRole.ADMIN:
            return User.objects.none()

        return User.objects.filter(
            tenant=self.request.user.tenant,
            role=UserRole.CUSTOMER
        )