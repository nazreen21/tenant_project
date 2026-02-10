# Third party modules
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.generics import ListAPIView
from rest_framework.exceptions import PermissionDenied

# Project modules
from apps.products.models import Product
from apps.products.api.v1.serializers import ProductClaimSerializer, ProductCreateSerializer,ProductUpdateSerializer,ProductListSerializer
from apps.accounts.models import UserRole


class ProductViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):

        user = self.request.user

        queryset = Product.objects.select_related(
            "company",
            "customer"
        ).filter(tenant=user.tenant)

        if user.role == UserRole.STAFF:
            return queryset.filter(company=user.company)

        if user.role == UserRole.CUSTOMER:
            return queryset.filter(customer=user)

        # admin / manager
        return queryset

    def get_serializer_class(self):

        if self.action == "create":
            return ProductCreateSerializer

        if self.action in ["update", "partial_update"]:
            return ProductUpdateSerializer

        return ProductListSerializer

    def perform_create(self, serializer):
        # Only staff can create products
        if self.request.user.role != UserRole.STAFF:
            raise PermissionDenied("Only staff can create products.")
        
        serializer.save()

    def perform_update(self, serializer):

        product = self.get_object()

        # prevent staff editing other company products
        if self.request.user.role == UserRole.STAFF:
            if product.company != self.request.user.company:
                raise PermissionDenied("Not allowed.")

        serializer.save()

class ProductClaimView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "product_claim"

    def post(self, request):

        serializer = ProductClaimSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        result = serializer.save()

        return Response(result)
    
class CustomerProductsView(ListAPIView):
    serializer_class = ProductListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):

        user = self.request.user

        if user.role != UserRole.ADMIN:
            raise PermissionDenied("Admin only.")

        return Product.objects.filter(
            tenant=user.tenant,
            customer_id=self.kwargs["id"]
        ).select_related("company", "customer")