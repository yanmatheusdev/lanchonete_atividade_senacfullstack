from django.contrib import admin

from .models import Categoria, Produto

admin.site.site_header = "Lanchonete - Painel Administrativo"
admin.site.site_title = "Lanchonete"
admin.site.index_title = "Gerenciar cardápio"


class ProdutoInline(admin.TabularInline):
    model = Produto
    extra = 1


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("nome", "descricao")
    search_fields = ("nome",)
    inlines = [ProdutoInline]


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ("nome", "preco", "categoria", "disponivel")
    list_filter = ("categoria", "disponivel")
    search_fields = ("nome",)
    list_editable = ("disponivel",)
    actions = ["marcar_indisponivel"]

    @admin.action(description="Marcar como indisponível")
    def marcar_indisponivel(self, request, queryset):
        qtd = queryset.update(disponivel=False)
        self.message_user(request, f"{qtd} produto(s) marcado(s) como indisponível.")
