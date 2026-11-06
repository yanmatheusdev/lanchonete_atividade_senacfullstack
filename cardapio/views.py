from django.db.models import ProtectedError
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Categoria, Produto
from .serializers import CategoriaSerializer, ProdutoSerializer


class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all().order_by("id")
    serializer_class = CategoriaSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["nome"]

    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except ProtectedError:
            return Response(
                {"detalhe": "Não é possível excluir: a categoria ainda tem produtos."},
                status=status.HTTP_409_CONFLICT,
            )

    @action(detail=True, methods=["get"])
    def produtos(self, request, pk=None):
        """GET /api/categorias/{id}/produtos/"""
        categoria = self.get_object()
        produtos = categoria.produtos.all().order_by("id")
        serializer = ProdutoSerializer(produtos, many=True)
        return Response(serializer.data)


class ProdutoViewSet(viewsets.ModelViewSet):
    serializer_class = ProdutoSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["nome"]

    def get_queryset(self):
        queryset = Produto.objects.select_related("categoria").order_by("id")
        disponivel = self.request.query_params.get("disponivel")
        if disponivel is not None:
            queryset = queryset.filter(disponivel=disponivel.lower() == "true")
        return queryset
