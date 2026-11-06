from django.db.models import ProtectedError
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from .ibge import IBGEIndisponivel, UFS_VALIDAS, listar_municipios
from .models import AreaEntrega, Categoria, Produto
from .serializers import (
    AreaEntregaSerializer,
    CategoriaSerializer,
    ProdutoSerializer,
)


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
        page = self.paginate_queryset(produtos)
        if page is not None:
            serializer = ProdutoSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
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
            disponivel = disponivel.lower()
            if disponivel not in {"true", "false"}:
                raise ValidationError({"disponivel": "Use 'true' ou 'false'."})
            queryset = queryset.filter(disponivel=disponivel == "true")
        return queryset


class AreaEntregaViewSet(viewsets.ModelViewSet):
    queryset = AreaEntrega.objects.all().order_by("municipio")
    serializer_class = AreaEntregaSerializer


class MunicipiosView(APIView):
    """GET /api/municipios/?uf=PE - consulta o IBGE."""

    def get(self, request):
        uf = request.query_params.get("uf", "").strip().upper()

        if not uf:
            return Response(
                {"erro": "Informe a UF. Exemplo: /api/municipios/?uf=PE"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if uf not in UFS_VALIDAS:
            return Response(
                {"erro": f"UF inválida: '{uf}'. Use a sigla de 2 letras."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            dados = listar_municipios(uf)
        except IBGEIndisponivel:
            return Response(
                {"erro": "Serviço do IBGE indisponível no momento. Tente mais tarde."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        if dados is None:
            return Response(
                {"erro": f"UF inválida: '{uf}'. Estado não encontrado no IBGE."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        municipios = [{"codigo_ibge": m["id"], "nome": m["nome"]} for m in dados]
        return Response({"uf": uf, "total": len(municipios), "municipios": municipios})
