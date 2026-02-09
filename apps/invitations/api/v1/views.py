# Third party modules
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.throttling import ScopedRateThrottle # Throttling to prevent from brute force attack

# Project modules
from apps.accounts.models import UserRole
from apps.invitations.api.v1.serializers import (AcceptInvitationSerializer,BootstrapAdminInvitationSerializer,ManagerInvitationSerializer)
from core.utils.permissions import IsAdmin, IsSuperAdmin


# Accept Invitation (public)
class AcceptInvitationView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope ="invitation_accept"

    def post(self, request):

        serializer = AcceptInvitationSerializer(data=request.data,context={"request": request})
        serializer.is_valid(raise_exception=True)

        result = serializer.save()

        return Response(result, status=status.HTTP_200_OK)

# Bootstrap admin invite(superadmin only)
class BootstrapAdminInvitationView(APIView):
    permission_classes = [IsAuthenticated,IsSuperAdmin]

    def post(self, request):

        serializer = BootstrapAdminInvitationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = serializer.save()

        return Response(result, status=status.HTTP_201_CREATED)

# Manager invite(admin only)
class ManagerInvitationView(APIView):
    permission_classes = [IsAuthenticated,IsAdmin]

    def post(self, request):

        serializer = ManagerInvitationSerializer(data=request.data,context={"request": request})
        serializer.is_valid(raise_exception=True)

        result = serializer.save()

        return Response(result, status=status.HTTP_201_CREATED)