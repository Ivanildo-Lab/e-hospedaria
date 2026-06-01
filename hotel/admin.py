from django.contrib import admin
from .models import CategoriaQuarto, Quarto

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