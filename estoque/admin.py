from django.contrib import admin
from .models import Produto, EstoqueFrigobar, MovimentacaoEstoque

@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'valor_custo', 'preco_venda', 'estoque_deposito', 'empresa')
    exclude = ('empresa',)

    def save_model(self, request, obj, form, change):
        obj.empresa = request.user.empresa
        super().save_model(request, obj, form, change)

@admin.register(EstoqueFrigobar)
class EstoqueFrigobarAdmin(admin.ModelAdmin):
    list_display = ('quarto', 'produto', 'quantidade_atual', 'capacidade_maxima')
    list_filter = ('quarto',)
    exclude = ('empresa',)

    def save_model(self, request, obj, form, change):
        obj.empresa = request.user.empresa
        super().save_model(request, obj, form, change)