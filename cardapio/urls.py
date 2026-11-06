from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AreaEntregaViewSet,
    CategoriaViewSet,
    MunicipioViewSet,
    ProdutoViewSet,
)

router = DefaultRouter()
router.register("categorias", CategoriaViewSet, basename="categoria")
router.register("produtos", ProdutoViewSet, basename="produto")
router.register("areas-entrega", AreaEntregaViewSet, basename="area-entrega")
router.register("municipios", MunicipioViewSet, basename="municipio")

urlpatterns = [
    path("", include(router.urls)),
]
