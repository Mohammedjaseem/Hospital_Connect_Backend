from django.db import models
from django_tenants.models import TenantMixin, DomainMixin
import uuid
from utils.multis3 import TenantMediaStorage

class Client(TenantMixin):
    id = models.AutoField(primary_key=True) # Primary key for the model
    name = models.CharField(max_length=100, unique=True, db_index=True)  # Ensuring unique client names
    is_active = models.BooleanField(default=True, db_index=True)  # Index for faster queries on active clients
    created_at = models.DateTimeField(auto_now_add=True)  # Use DateTime for consistent timestamps
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Domain(DomainMixin):
    pass


class Organizations(models.Model):
    client = models.OneToOneField(Client, on_delete=models.CASCADE, related_name="organization")
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    name = models.CharField(max_length=550, unique=True, db_index=True)  # Unique and indexed for frequent lookups
    address = models.TextField()
    phone_number = models.CharField(max_length=15, unique=True)
    email_domain = models.CharField(max_length=50, null=True, blank=True)  # Extended max length for flexibility
    hr_email = models.EmailField(null=True, blank=True)
    staff_group_email = models.EmailField(null=True, blank=True)
    management_group_email = models.EmailField(null=True, blank=True)
    suggestions_emails = models.TextField(null=True, blank=True)
    hr_mobile = models.CharField(max_length=15, null=True, blank=True)
    website = models.URLField(max_length=200, null=True, blank=True)
    short_code = models.CharField(max_length=10, unique=True, db_index=True)
    logo = models.ImageField(storage=TenantMediaStorage(), upload_to="Organizations/Logo/", null=True, blank=True)
    email_banner = models.ImageField(storage=TenantMediaStorage() ,upload_to="Organizations/Email_Banner/", null=True, blank=True)
    org_connect_domain = models.CharField(
        max_length=100, default="Connect Domain not added!", db_index=True
    )  # Indexed for domain-specific queries
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Organization"
        verbose_name_plural = "Organizations"
        indexes = [
            models.Index(fields=["uuid"]),
            models.Index(fields=["name"]),
            models.Index(fields=["short_code"]),
        ]

    def __str__(self):
        return self.name
