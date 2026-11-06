from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AreaEntregaViewSet,
    CategoriaViewSet,
    MunicipiosView,
    ProdutoViewSet,
)

router = DefaultRouter()
router.register("categorias", CategoriaViewSet, basename="categoria")
router.register("produtos", ProdutoViewSet, basename="produto")
router.register("areas-entrega", AreaEntregaViewSet, basename="area-entrega")

urlpatterns = [
    path("municipios/", MunicipiosView.as_view(), name="municipios"),
    path("", include(router.urls)),
]
