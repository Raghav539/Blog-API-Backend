from django.db import models
import uuid
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone

from .managers import UserManager  

class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User Model
    - Replaces username with email
    - Supports extra fields (phone, profile image, roles)
    """
    # Remove default username field
    username = None
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, unique=True)

    # Core fields
    email = models.EmailField(
        unique=True,
        max_length=255,
        help_text="User login email"
    )
    phone = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        help_text="User phone number"
    )

    # User status flags
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)  # Already in PermissionsMixin, but okay to redefine

    # Date fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Profile
    profile_image = models.ImageField(
        upload_to="users/profile/",
        blank=True,
        null=True
    )

    # Role system - Fixed typo: CharFeild → CharField
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('editor', 'Editor'),
        ('author', 'Author'),
        ('reader', 'Reader'),
    ]
    role = models.CharField(
        max_length=50,
        choices=ROLE_CHOICES,
        default='reader'
    )

    # Two Factor Authentication
    is_2fa_enabled = models.BooleanField(default=False)
    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_created_at = models.DateTimeField(blank=True, null=True)

    # Manager
    objects = UserManager()

    # Authentication settings
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []  # No additional fields required when creating superuser

    def __str__(self):
        return self.email

    def is_otp_valid(self):
        if not self.otp_created_at:
            return False
        return timezone.now() < (self.otp_created_at + timezone.timedelta(minutes=10))

class LoginActivity(models.Model):
    """
    Stores login activity details:
    - IP address
    - Location (city, region, country)
    - Device/User-Agent
    - Timestamp
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="login_logs")

    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True, null=True)

    country = models.CharField(max_length=100, blank=True, null=True)
    region = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)

    login_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} logged in from {self.ip_address}"
    
    
class EmailOTP(models.Model):
    """
    Stores OTPs sent to users for email verification or password reset.
    - OTP code
    - Associated user
    - Creation timestamp
    - Expiration timestamp
    """
    email = models.EmailField()
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    
    def is_valid(self):
        return (not self.is_used) and (timezone.now() < self.expires_at)
    
    def __str__(self):
        return f"OTP for {self.email}: {self.otp}"
    
    class Meta:
        ordering = ['-created_at']