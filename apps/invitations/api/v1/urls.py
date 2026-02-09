# Django modules
from django.urls import path

# Project modules
from apps.invitations.api.v1.views import (AcceptInvitationView,BootstrapAdminInvitationView,ManagerInvitationView)

urlpatterns = [
    # Public
    path("accept/", AcceptInvitationView.as_view(), name="accept-invitation"),

    # superadmin
    path("bootstrap-admin/",BootstrapAdminInvitationView.as_view(),name="bootstrap-admin-invite"),

    # admin
    path("",ManagerInvitationView.as_view(),name="manager-invite"),
]