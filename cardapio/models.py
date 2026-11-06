from django.core.validators import MinValueValidator
from django.db import models


class Categoria(models.Model):
    nome = models.CharField(max_length=100, unique=True)
    descricao = models.TextField(blank=True)

    def __str__(self):
        return self.nome


class Produto(models.Model):
    nome = models.CharField(max_length=150)
    preco = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    disponivel = models.BooleanField(default=True)
    # PROTECT: não deixa excluir uma categoria que ainda tem produtos.
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,
        related_name="produtos",
    )

    def __str__(self):
        return self.nome
