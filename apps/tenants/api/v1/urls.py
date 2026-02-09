# django modules
from django.urls import path, include
# Third party modules
from rest_framework.routers import DefaultRouter
#Project modules
from apps.tenants.api.v1.views import TenantMeView, CompanyViewSet

router = DefaultRouter()
router.register("companies", CompanyViewSet, basename="companies")

urlpatterns = [

    # Tenant URL endpoints
    path("me/", TenantMeView.as_view()),   # GET and PATCH tenants endpoint

    # Companies URL endpoint
    path("", include(router.urls)),
]