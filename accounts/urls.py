from django.urls import path
from .views import (
    RegisterAPIView,
    LoginAPIView,
    VerifyOTPAPIView,
    LogoutAPIView,
    LoginHistoryAPIView
)

urlpatterns = [
    path("register/", RegisterAPIView.as_view()),
    path("login/", LoginAPIView.as_view()),
    path("verify-otp/", VerifyOTPAPIView.as_view()),
    path("logout/", LogoutAPIView.as_view()),
    path("login-history/", LoginHistoryAPIView.as_view()),
]
