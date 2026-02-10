# Third party modules
from rest_framework.routers import DefaultRouter

# Project modules
from apps.products.api.v1.views import ProductViewSet

# Django modules
from django.urls import path, include

router = DefaultRouter()
router.register("", ProductViewSet, basename="products")

urlpatterns = [
    path("", include(router.urls)),
]