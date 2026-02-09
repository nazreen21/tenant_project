import uuid
from django.db import models
from apps.common.models import BaseModel

# Tenant model
class Tenant(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

# Company model    
class Company(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant,on_delete=models.CASCADE,related_name="companies",db_index=True)
    name = models.CharField(max_length=255)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "name"],
                name="unique_company_per_tenant"
            )
        ]

    def __str__(self):
        return f"{self.name} ({self.tenant.name})"