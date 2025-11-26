from django.urls import path

from .views import (
    RegisterAPIView,
    LoginAPIView,
    VerifyOTPAPIView,
    LogoutAPIView,
    LoginHistoryAPIView,
    ProfileAPIView,
    ProfileUpdateAPIView,
    ProfileImageUploadAPIView,
    ProfileImageDeleteAPIView, ChangePasswordView,
)

urlpatterns = [
    path("register/", RegisterAPIView.as_view(), name="register"),
    path("login/", LoginAPIView.as_view(), name="login"),
    path("verify-otp/", VerifyOTPAPIView.as_view(), name="verify-otp"),
    path("logout/", LogoutAPIView.as_view(), name="logout"),
    path("login-history/", LoginHistoryAPIView.as_view(), name="login-history"),
    path("change-password/", ChangePasswordView(), name="change-password"),

    path("profile/view/", ProfileAPIView.as_view(), name="profile-view"),
    path("profile/update/", ProfileUpdateAPIView.as_view(), name="profile-update"),
    path("profile/upload-image/", ProfileImageUploadAPIView.as_view(), name="profile-upload-image"),
    path("profile/delete-image/", ProfileImageDeleteAPIView.as_view(), name="profile-delete-image"),
]
