import uuid
import secrets

#Django modules
from django.db import models
from django.core.exceptions import ValidationError

#Project modules
from apps.common.models import BaseModel
from apps.tenants.models import Tenant, Company
from apps.accounts.models import User, UserRole


#Product model
class Product(BaseModel):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant,on_delete=models.CASCADE,related_name="products",db_index=True)
    company = models.ForeignKey(Company,on_delete=models.CASCADE,related_name="products")
    created_by = models.ForeignKey(User,on_delete=models.CASCADE,related_name="created_products")
    customer = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True,related_name="customer_products")
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    share_token = models.CharField(max_length=255,unique=True,db_index=True)

    # Auto-generate token
    def save(self, *args, **kwargs):

        if not self.share_token:
            self.share_token = secrets.token_urlsafe(48)

        self.full_clean()
        super().save(*args, **kwargs)

    # Constraints
    def clean(self):

        # must be staff
        if self.created_by.role != UserRole.STAFF:
            raise ValidationError("Only staff can create products.")

        # tenant must match
        if self.tenant != self.created_by.tenant:
            raise ValidationError("Tenant mismatch.")

        # company must match
        if self.company != self.created_by.company:
            raise ValidationError("Company mismatch.")

        # customer tenant must match
        if self.customer and self.customer.tenant != self.tenant:
            raise ValidationError("Customer tenant mismatch.")

    def __str__(self):
        return self.name