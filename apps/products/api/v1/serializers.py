# Third party modules
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

# Project modules
from apps.products.models import Product
from apps.accounts.models import UserRole

# Django modules
from django.contrib.auth import get_user_model

User = get_user_model()

class ProductCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = ["id", "name", "description", "share_token"]
        read_only_fields = ["id", "share_token"]

    def create(self, validated_data):

        user = self.context["request"].user

        return Product.objects.create(
            tenant=user.tenant,
            company=user.company,
            created_by=user,
            **validated_data
        )
    
class ProductUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = ["name", "description"]

class ProductListSerializer(serializers.ModelSerializer):

    company_name = serializers.CharField(source="company.name", read_only=True)
    customer_email = serializers.EmailField(source="customer.email", read_only=True)

    class Meta:
        model = Product
        fields = ["id","name","company_name","customer_email","created_at"]

class ProductClaimSerializer(serializers.Serializer):
    share_token = serializers.CharField()
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, required=True, allow_blank=False)

    def validate(self, attrs):

        try:
            product = Product.objects.get(
                share_token=attrs["share_token"]
            )
        except Product.DoesNotExist:
            raise serializers.ValidationError("Invalid token.")

        attrs["product"] = product
        return attrs

    def create(self, validated_data):

        product = validated_data["product"]
        email = validated_data["email"]
        password = validated_data["password"]

        # Check if user already exists
        try:
            user = User.objects.get(email=email)
            # User exists - verify password
            if not user.check_password(password):
                raise serializers.ValidationError("Invalid password.")
        except User.DoesNotExist:
            # User doesn't exist - create new user with password
            user = User.objects.create_user(
                email=email,
                password=password,
                role=UserRole.CUSTOMER,
                tenant=product.tenant
            )

        product.customer = user
        product.save()

        refresh = RefreshToken.for_user(user)

        return {
            "detail": "Claimed.",
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }