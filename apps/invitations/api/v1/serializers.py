# Python modules
from datetime import timedelta

# Django modules
from django.utils import timezone
from django.db import transaction
from django.contrib.auth import get_user_model

# Third-party modules
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

# Project modules
from apps.invitations.models import Invitation
from apps.tenants.models import Tenant
from apps.accounts.models import UserRole

User = get_user_model()

# Accept Invitation
class AcceptInvitationSerializer(serializers.Serializer):
    token = serializers.CharField()
    tenant_name = serializers.CharField(required=False)
    password = serializers.CharField(write_only=True, min_length=8)

    def validate(self, attrs):

        token = attrs.get("token")

        try:
            invitation = Invitation.objects.get(token=token)
        except Invitation.DoesNotExist:
            raise serializers.ValidationError("Invalid invitation token.")

        if invitation.is_used:
            raise serializers.ValidationError("Invitation already used.")

        if invitation.is_expired:
            raise serializers.ValidationError("Invitation expired.")

        # tenant required only for bootstrap admin
        if invitation.role == UserRole.ADMIN and not attrs.get("tenant_name"):
            raise serializers.ValidationError(
                {"tenant_name": "Tenant name is required."}
            )

        attrs["invitation"] = invitation
        return attrs

    def create(self, validated_data):

        invitation = validated_data["invitation"]
        password = validated_data["password"]
        tenant_name = validated_data.get("tenant_name")

        with transaction.atomic():

            # bootstrap admin
            if invitation.role == UserRole.ADMIN:

                tenant = Tenant.objects.create(name=tenant_name)

                user = User.objects.create_user(
                    email=invitation.email,
                    password=password,
                    role=UserRole.ADMIN,
                    tenant=tenant,
                )

            # manager
            else:

                tenant = invitation.tenant

                user = User.objects.create_user(
                    email=invitation.email,
                    password=password,
                    role=UserRole.MANAGER,
                    tenant=tenant,
                )

            invitation.used_at = timezone.now()
            invitation.save()

        refresh = RefreshToken.for_user(user)

        return {
            "detail": "Invitation accepted.",
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }

# Bootstrap admin invite
class BootstrapAdminInvitationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    expires_in_hours = serializers.IntegerField(default=48)

    def create(self, validated_data):

        expires_at = timezone.now() + timedelta(
            hours=validated_data["expires_in_hours"]
        )

        invitation = Invitation.objects.create(
            email=validated_data["email"],
            role=UserRole.ADMIN,
            expires_at=expires_at,
            tenant=None,  # bootstrap
        )

        return {
            "invitation_token": invitation.token
        }

# Manager invite
class ManagerInvitationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    expires_in_hours = serializers.IntegerField(default=48)

    def create(self, validated_data):

        request = self.context["request"]

        expires_at = timezone.now() + timedelta(
            hours=validated_data["expires_in_hours"]
        )

        invitation = Invitation.objects.create(
            email=validated_data["email"],
            role=UserRole.MANAGER,
            tenant=request.user.tenant,
            expires_at=expires_at,
        )

        return {
            "invitation_token": invitation.token
        }