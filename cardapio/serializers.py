from rest_framework import serializers

from .ibge import IBGEIndisponivel, municipio_existe
from .models import AreaEntrega, Categoria, Produto


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ["id", "nome", "descricao"]


class ProdutoSerializer(serializers.ModelSerializer):
    categoria_nome = serializers.CharField(source="categoria.nome", read_only=True)

    class Meta:
        model = Produto
        fields = ["id", "nome", "preco", "disponivel", "categoria", "categoria_nome"]

    def validate_preco(self, value):
        if value < 0:
            raise serializers.ValidationError("O preço não pode ser negativo.")
        return value


class AreaEntregaSerializer(serializers.ModelSerializer):
    class Meta:
        model = AreaEntrega
        fields = ["id", "municipio", "codigo_ibge", "taxa_entrega"]

    def validate_codigo_ibge(self, value):
        try:
            existe = municipio_existe(value)
        except IBGEIndisponivel:
            raise serializers.ValidationError(
                "Não foi possível validar o código no IBGE agora. Tente novamente."
            )
        if not existe:
            raise serializers.ValidationError("Código IBGE inexistente.")
        return value
