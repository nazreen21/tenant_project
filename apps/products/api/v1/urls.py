# Third party modules
from rest_framework.routers import DefaultRouter

# Project modules
from apps.products.api.v1.views import CustomerProductsView, ProductViewSet, ProductClaimView

# Django modules
from django.urls import path, include

router = DefaultRouter()
router.register("", ProductViewSet, basename="products")

urlpatterns = [
    path("", include(router.urls)),
    path("public/products/claim/", ProductClaimView.as_view()),
    path("admin/customers/<uuid:id>/products/",CustomerProductsView.as_view()),
]