from django.contrib import admin
from .models import Cadastro, CategoriaCadastro

@admin.register(Cadastro)
class CadastroAdmin(admin.ModelAdmin):
    list_display = ('nome', 'papel', 'tipo_pessoa', 'celular', 'situacao')
    list_filter = ('situacao', 'papel', 'tipo_pessoa')
    search_fields = ('nome', 'cpf', 'cnpj')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser: return qs
        return qs.filter(empresa=request.user.empresa)

    def save_model(self, request, obj, form, change):
        if not obj.empresa_id:
            obj.empresa = request.user.empresa
        super().save_model(request, obj, form, change)