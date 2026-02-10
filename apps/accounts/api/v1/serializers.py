# Django modules
from django.contrib.auth import authenticate
from django.utils import timezone
from django.contrib.auth import get_user_model

# Third-party modules
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import timedelta

#project modules
from apps.accounts.models import PasswordResetToken, UserRole

User = get_user_model()

# login serializer
class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        user = authenticate(username=email,password=password)

        if not user:
            raise serializers.ValidationError("Invalid credentials.")

        if not user.is_active:
            raise serializers.ValidationError("User account is disabled.")

        attrs["user"] = user
        return attrs

    def create(self, validated_data):
        user = validated_data["user"]
        refresh = RefreshToken.for_user(user)

        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }
#Password reset request serializer
class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def create(self, validated_data):

        email = validated_data["email"]

        user = User.objects.filter(email=email).first()

        # Never reveal if user exists
        if user:

            # invalidate previous tokens
            PasswordResetToken.objects.filter(
                user=user,
                used_at__isnull=True
            ).update(used_at=timezone.now())

            reset = PasswordResetToken.objects.create(
                user=user,
                expires_at=timezone.now() + timedelta(hours=1)
            )

            token = reset.token
        else:
            token = "dummy-token-for-demo"

        return {
            "detail": "If the email exists, a reset token has been generated.",
            "reset_token": token
        }

# password reset confirm serializer   
class PasswordResetConfirmSerializer(serializers.Serializer):
    reset_token = serializers.CharField()
    new_password = serializers.CharField(write_only=True, min_length=8)

    def validate(self, attrs):

        token = attrs["reset_token"]

        try:
            reset = PasswordResetToken.objects.get(token=token)
        except PasswordResetToken.DoesNotExist:
            raise serializers.ValidationError("Invalid reset token.")

        if reset.is_used:
            raise serializers.ValidationError("Token already used.")

        if reset.is_expired:
            raise serializers.ValidationError("Token expired.")

        attrs["reset"] = reset
        return attrs

    def create(self, validated_data):

        reset = validated_data["reset"]
        user = reset.user
        password = validated_data["new_password"]

        user.set_password(password)
        user.save()

        reset.used_at = timezone.now()
        reset.save()

        return {
            "detail": "Password updated."
        }
    
# Staff serializer
class StaffSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source="company.name",read_only=True)

    class Meta:
        model = User
        fields = ["id","email","password","company","company_name",]
        extra_kwargs = {
            "password": {"write_only": True}
        }

    def create(self, validated_data):
        request = self.context["request"]
        company = validated_data["company"]

        # tenant safety
        if company.tenant != request.user.tenant:
            raise serializers.ValidationError("Invalid company.")

        return User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            role=UserRole.STAFF,
            tenant=request.user.tenant,
            company=company
        )
    
# Customer serializer 
class CustomerSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ["id", "email", "created_at"]