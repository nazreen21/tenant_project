# Thirdparty modules
from rest_framework import serializers

# project modules
from apps.tenants.models import Company, Tenant

class TenantSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tenant
        fields = ["id", "name", "created_at"]
        read_only_fields = ["id", "name"]

class CompanySerializer(serializers.ModelSerializer):

    class Meta:
        model = Company
        fields = ["id", "name", "created_at"]
        read_only_fields = ["id"]