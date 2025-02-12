from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
import uuid
from django.contrib.auth.models import Group, Permission
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password
from app.models import Organizations


class CustomUserManager(BaseUserManager):
    def create_user(self, email, org, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, org=org, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, org, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        # Fetch organization instance if organization is provided as an ID
        # This is useful when creating superusers using the shell or terminal
        if isinstance(org, int):
            organization = Organizations.objects.get(pk=org)

        return self.create_user(email=email, org=organization, password=password, **extra_fields)
    
class UserType(models.Model):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=25, unique=True)
    desc = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'User Type'
        verbose_name_plural = 'User Types'
        indexes = [
            models.Index(fields=['name']),
        ]

class CustomUser(AbstractBaseUser, PermissionsMixin):
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    org = models.ForeignKey(Organizations, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    user_type = models.ForeignKey(UserType, on_delete=models.SET_NULL, null=True,blank=True)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_school_admin = models.BooleanField(default=False)
    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['org']

    groups = models.ManyToManyField(Group, related_name='customuser_groups', blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name='customuser_permissions', blank=True)

    class Meta:
        verbose_name = 'Accounts'
        verbose_name_plural = 'Accounts'
        indexes = [
            models.Index(fields=['org']),
            models.Index(fields=['uuid']),
            models.Index(fields=['email']),
            models.Index(fields=['is_verified']),
            models.Index(fields=['user_type']),
        ]

    def __str__(self):
        return f"{self.id} | {self.email}"


def get_expiry_time():
    return timezone.now() + timedelta(minutes=5)


class OTP(models.Model):
    user = models.ForeignKey("CustomUser", on_delete=models.CASCADE, related_name="otps")
    otp_hash = models.CharField(max_length=128) 
    expires_at = models.DateTimeField(default=get_expiry_time)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "OTP"
        verbose_name_plural = "OTPs"
        indexes = [
            models.Index(fields=["user"]),
            models.Index(fields=["expires_at"]),
        ]

    def save(self, *args, **kwargs):
        # Automatically set expiration if not provided
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(minutes=5)
        super().save(*args, **kwargs)

    def set_otp(self, otp):
        """Hash the OTP before saving."""
        self.otp_hash = make_password(otp)

    def verify_otp(self, otp):
        """Verify the provided OTP against the stored hash."""
        return check_password(otp, self.otp_hash)

    def is_expired(self):
        """Check if the OTP has expired."""
        return timezone.now() > self.expires_at

    def __str__(self):
        return f"OTP for {self.user.email} - Verified: {self.is_verified}"