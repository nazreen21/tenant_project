import uuid
import secrets

# Django modules
from django.db import models
from django.utils import timezone

# Project modules
from apps.common.models import BaseModel
from apps.tenants.models import Tenant
from apps.accounts.models import UserRole


class Invitation(BaseModel):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    email = models.EmailField(db_index=True)

    role = models.CharField(
        max_length=20,
        choices=[
            (UserRole.ADMIN, "Admin"),
            (UserRole.MANAGER, "Manager"),
        ],
    )

    tenant = models.ForeignKey(Tenant,on_delete=models.CASCADE,null=True,blank=True,related_name="invitations")
    token = models.CharField(max_length=255,unique=True,db_index=True)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):

        if not self.token:
            self.token = secrets.token_urlsafe(48)
        
        self.full_clean()

        super().save(*args, **kwargs)

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at

    @property
    def is_used(self):
        return self.used_at is not None
    