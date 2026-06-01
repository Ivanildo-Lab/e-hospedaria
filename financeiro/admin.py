from django.contrib import admin
from .models import PlanoDeContas, Caixa, Conta, Lancamento

class FinanceiroSaaSAdmin(admin.ModelAdmin):
    def get_exclude(self, request, obj=None):
        return [] if request.user.is_superuser else ['empresa']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser: return qs
        return qs.filter(empresa=request.user.empresa)

    def save_model(self, request, obj, form, change):
        if not obj.empresa_id:
            obj.empresa = request.user.empresa
        super().save_model(request, obj, form, change)

@admin.register(PlanoDeContas)
class PlanoDeContasAdmin(FinanceiroSaaSAdmin):
    list_display = ('codigo', 'nome', 'tipo', 'empresa')

@admin.register(Caixa)
class CaixaAdmin(FinanceiroSaaSAdmin):
    list_display = ('nome', 'saldo_inicial', 'empresa')

@admin.register(Conta)
class ContaAdmin(FinanceiroSaaSAdmin):
    list_display = ('descricao', 'cadastro', 'valor', 'data_vencimento', 'status')
    list_filter = ('status', 'data_vencimento')

@admin.register(Lancamento)
class LancamentoAdmin(FinanceiroSaaSAdmin):
    list_display = ('data_lancamento', 'descricao', 'valor', 'caixa')