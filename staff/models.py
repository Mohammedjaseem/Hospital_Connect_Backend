import uuid
from django.db import models
from django.utils.timezone import now
from django.utils.safestring import mark_safe
from datetime import date
from utils.multis3 import TenantMediaStorage
from utils.image_compressor import ImageCompressorMixin
from utils.choices import GenderChoices, BloodGroupChoices



class StaffProfile(models.Model, ImageCompressorMixin):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    is_active = models.BooleanField(default=True)
    user = models.OneToOneField(
        "custom_users.CustomUser",
        on_delete=models.CASCADE,
        related_name="staff_profile",
    )
    emp_id = models.CharField(max_length=50, unique=True, db_index=True)
    name = models.CharField(max_length=250)
    gender = models.CharField(
        max_length=10, choices=GenderChoices.CHOICES, blank=True, null=True
    )
    dob = models.DateField(blank=True, null=True)
    mobile = models.CharField(max_length=15, unique=True)
    department = models.ForeignKey(
        "administration.Departments", on_delete=models.SET_NULL, null=True, blank=True
    )
    designation = models.ForeignKey(
        "administration.Designations", on_delete=models.SET_NULL, null=True, blank=True
    )
    is_verified = models.BooleanField(default=False)
    is_hosteller = models.BooleanField(default=False)

    # Store images in tenant-specific S3 folders
    picture = models.ImageField(
        storage=TenantMediaStorage(), upload_to="users/picture", blank=True, null=True
    )

    address = models.TextField(blank=True, null=True)
    blood_group = models.CharField(
        max_length=3, choices=BloodGroupChoices.CHOICES, blank=True, null=True
    )
    emergency_contact = models.CharField(max_length=15, blank=True, null=True)
    created_at = models.DateTimeField(default=now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def get_default_picture_url(self):
        return "https://cdn.vectorstock.com/i/preview-1x/82/99/no-image-available-like-missing-picture-vector-43938299.jpg"

    def profile_pic(self):
        img_url = self.picture.url if self.picture else self.get_default_picture_url()
        return mark_safe(
            f'<img src="{img_url}" width="80" height="80" style="border-radius: 15px;" />'
        )

    def calculate_age(self):
        if self.dob:
            today = date.today()
            return (
                today.year
                - self.dob.year
                - ((today.month, today.day) < (self.dob.month, self.dob.day))
            )
        return None

    def save(self, *args, **kwargs):
        if self.picture:
            self.compress_image()  # Apply compression if necessary
        super().save(*args, **kwargs)

    @property
    def age(self):
        return self.calculate_age()
