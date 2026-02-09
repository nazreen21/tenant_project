import uuid
import secrets

# Django modules 
from django.db import models
from django.contrib.auth.models import (AbstractBaseUser,PermissionsMixin,BaseUserManager)
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.conf import settings

# Project modules
from apps.common.models import BaseModel
from apps.tenants.models import Tenant, Company


# Roles
class UserRole(models.TextChoices):
    SUPERADMIN = "SUPERADMIN", "Super Admin"
    ADMIN = "ADMIN", "Admin"
    MANAGER = "MANAGER", "Manager"
    STAFF = "STAFF", "Staff"
    CUSTOMER = "CUSTOMER", "Customer"


# Custom User Manager
class UserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):

        if not email:
            raise ValueError("Email is required")

        email = self.normalize_email(email)

        user = self.model(email=email, **extra_fields)
        user.set_password(password)

        # triggers model validation 
        user.full_clean()

        user.save(using=self._db)
        return user


    def create_superuser(self, email, password=None, **extra_fields):

        extra_fields.setdefault("role", UserRole.SUPERADMIN)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("tenant", None)
        extra_fields.setdefault("company", None)

        if extra_fields.get("role") != UserRole.SUPERADMIN:
            raise ValueError("Superuser must have SUPERADMIN role.")

        return self.create_user(email, password, **extra_fields)


# User model
class User(AbstractBaseUser, PermissionsMixin, BaseModel):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, db_index=True)
    role = models.CharField(max_length=20,choices=UserRole.choices)
    tenant = models.ForeignKey(Tenant,on_delete=models.CASCADE,null=True,blank=True,related_name="users")
    company = models.ForeignKey(Company,on_delete=models.CASCADE,null=True,blank=True,related_name="users")

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # manager
    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []   # important for createsuperuser

    # model constraints
    def clean(self):

        # STAFF must belong to company
        if self.role == UserRole.STAFF and not self.company:
            raise ValidationError("Staff must belong to a company.")

        # Non-staff must not have company
        if self.role in [
            UserRole.ADMIN,
            UserRole.MANAGER,
            UserRole.CUSTOMER
        ] and self.company:
            raise ValidationError("Only staff can be assigned to a company.")

        # Everyone except SUPERADMIN must belong to tenant
        if self.role != UserRole.SUPERADMIN and not self.tenant:
            raise ValidationError("User must belong to a tenant.")

        # Company tenant must match user tenant
        if self.company and self.company.tenant != self.tenant:
            raise ValidationError("Company tenant must match user tenant.")

    def save(self, *args, **kwargs):
        # ensure validation always runs
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.email} ({self.role})"

#PasswordResetToken model   
class PasswordResetToken(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="reset_tokens")
    token = models.CharField(max_length=255, unique=True, db_index=True)
    expires_at = models.DateTimeField()
    used_at = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):

        if not self.token:
            self.token = secrets.token_urlsafe(48)

        super().save(*args, **kwargs)

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at

    @property
    def is_used(self):
        return self.used_at is not None