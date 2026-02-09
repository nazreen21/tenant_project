# Django module
from django.urls import path

# Third party module
from rest_framework_simplejwt.views import TokenRefreshView

#Project module
from apps.accounts.api.v1.views import CustomerListView, LoginView, PasswordResetConfirmView, PasswordResetRequestView, StaffView

urlpatterns = [
    # Auth #

    #login url endpoint
    path("login/", LoginView.as_view(), name="login"), 
    #refresh token endpoint
    path("token/refresh/", TokenRefreshView.as_view()),
    # password reset request endpoint
    path("password-reset/request/",PasswordResetRequestView.as_view(),name="password-reset-request"),
    # password reset confirm endpoint
    path("password-reset/confirm/",PasswordResetConfirmView.as_view(),name="password-reset-confirm"),

    # Staff #
    path("staff/", StaffView.as_view()),

    # Admin #
    path("admin/customers/", CustomerListView.as_view()),
]