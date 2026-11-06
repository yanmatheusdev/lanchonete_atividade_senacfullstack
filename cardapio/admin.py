from django.contrib import admin

from .models import Categoria, Produto


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("nome", "descricao")
    search_fields = ("nome",)


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ("nome", "preco", "categoria", "disponivel")
    list_filter = ("categoria", "disponivel")
    search_fields = ("nome",)
    list_editable = ("disponivel",)
