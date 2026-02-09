
# Third party modules
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied

# project modules
from apps.accounts.models import UserRole
from apps.tenants.api.v1.serializers import CompanySerializer, TenantSerializer
from apps.tenants.models import Company

class TenantMeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):

        if request.user.role not in [UserRole.ADMIN, UserRole.MANAGER]:
            raise PermissionDenied("Not allowed.")

        serializer = TenantSerializer(request.user.tenant)
        return Response(serializer.data)

    def patch(self, request):

        if request.user.role != UserRole.ADMIN:
            raise PermissionDenied("Only admin can update tenant.")

        tenant = request.user.tenant

        serializer = TenantSerializer(tenant,data=request.data,partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)
    
class CompanyViewSet(ModelViewSet):
    serializer_class = CompanySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):

        user = self.request.user

        if user.role not in [UserRole.ADMIN, UserRole.MANAGER]:
            raise PermissionDenied("Not allowed.")

        return Company.objects.filter(
            tenant=user.tenant
        ).order_by("-created_at")

    def perform_create(self, serializer):
        serializer.save(tenant=self.request.user.tenant)

    def perform_update(self, serializer):

        company = self.get_object()

        if company.tenant != self.request.user.tenant:
            raise PermissionDenied("Tenant mismatch.")

        serializer.save()