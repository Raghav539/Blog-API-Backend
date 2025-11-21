from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone

from .managers import UserManager  # Fixed: space before "managers"


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom User Model
    - Replaces username with email
    - Supports extra fields (phone, profile image, roles)
    """

    # Remove default username field
    username = None

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