from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, LoginActivity, EmailOTP

# ----------------------------
# Custom User Admin
# ----------------------------
@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    list_display = (
        "email",
        "full_name",
        "role",
        "is_staff",
        "is_active",
        "otp",  # show current OTP
    )
    list_filter = ("is_staff", "is_active", "role")
    search_fields = ("email", "full_name", "otp")
    ordering = ("email",)
    readonly_fields = (
        "otp",
        "otp_created_at",
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (None, {"fields": ("email", "full_name", "password")}),
        ("Permissions", {"fields": ("role", "is_staff", "is_active", "is_superuser")}),
        ("2FA / OTP", {"fields": ("is_2fa_enabled", "otp", "otp_created_at")}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
        ("Profile", {"fields": ("profile_image",)}),
    )


# ----------------------------
# Login Activity Admin
# ----------------------------
@admin.register(LoginActivity)
class LoginActivityAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "ip_address",
        "city",
        "region",
        "country",
        "latitude",
        "longitude",
        "device",
        "login_time",
    )
    search_fields = ("user__email", "ip_address", "city", "region", "country", "device")
    list_filter = ("city", "region", "country")
    readonly_fields = (
        "user",
        "ip_address",
        "city",
        "region",
        "country",
        "latitude",
        "longitude",
        "device",
        "login_time",
    )


# ----------------------------
# Email OTP Admin
# ----------------------------
@admin.register(EmailOTP)
class EmailOTPAdmin(admin.ModelAdmin):
    list_display = ("email", "otp", "created_at", "expires_at", "is_used")
    search_fields = ("email", "otp")
    list_filter = ("is_used",)
    readonly_fields = ("created_at",)
