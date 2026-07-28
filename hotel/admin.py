from django.contrib import admin
from .models import CategoriaQuarto, Quarto, Hospedagem, ConsumoHospedagem, FaixaPrecoCategoria

@admin.register(CategoriaQuarto)
class CategoriaQuartoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'preco_diaria', 'preco_hora', 'empresa')
    exclude = ('empresa',)

    def save_model(self, request, obj, form, change):
        obj.empresa = request.user.empresa
        super().save_model(request, obj, form, change)

@admin.register(Quarto)
class QuartoAdmin(admin.ModelAdmin):
    list_display = ('numero', 'categoria', 'status', 'empresa')
    exclude = ('empresa',)
    list_editable = ('status',)

    def save_model(self, request, obj, form, change):
        obj.empresa = request.user.empresa
        super().save_model(request, obj, form, change)

@admin.register(FaixaPrecoCategoria)
class FaixaPrecoCategoriaAdmin(admin.ModelAdmin):
    list_display = ('categoria', 'qtd_hospedes', 'preco_diaria', 'preco_hora', 'empresa')
    exclude = ('empresa',)

    def save_model(self, request, obj, form, change):
        obj.empresa = request.user.empresa
        super().save_model(request, obj, form, change)

@admin.register(Hospedagem)
class HospedagemAdmin(admin.ModelAdmin):
    list_display = ('quarto', 'hospede', 'tipo', 'quantidade_hospedes', 'ativa', 'empresa')
    list_filter = ('ativa', 'tipo')
    exclude = ('empresa',)

    def save_model(self, request, obj, form, change):
        obj.empresa = request.user.empresa
        super().save_model(request, obj, form, change)

@admin.register(ConsumoHospedagem)
class ConsumoHospedagemAdmin(admin.ModelAdmin):
    list_display = ('hospedagem', 'produto', 'quantidade', 'valor_unitario', 'total', 'empresa')
    exclude = ('empresa',)

    def save_model(self, request, obj, form, change):
        obj.empresa = request.user.empresa
        super().save_model(request, obj, form, change)