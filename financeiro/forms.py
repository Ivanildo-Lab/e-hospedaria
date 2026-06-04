from django import forms
from .models import Conta, Lancamento, Caixa, PlanoDeContas, FormaPagamento
from cadastros.models import Cadastro

# --- FORMULÁRIO DE CAIXA / BANCO ---
class CaixaForm(forms.ModelForm):
    class Meta:
        model = Caixa
        fields = ['nome', 'saldo_inicial']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'w-full bg-white border-2 border-slate-200 p-3 rounded-xl focus:border-blue-500 outline-none transition-all'
            })

# --- FORMULÁRIO DE PLANO DE CONTAS ---
class PlanoContasForm(forms.ModelForm):
    class Meta:
        model = PlanoDeContas
        fields = ['codigo', 'nome', 'tipo']
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'w-full bg-white border-2 border-slate-200 p-3 rounded-xl focus:border-blue-500 outline-none transition-all'
            })

    def clean_codigo(self):
        codigo = self.cleaned_data.get('codigo')
        if self.user and codigo:
            existe = PlanoDeContas.objects.filter(
                empresa=self.user.empresa,
                codigo=codigo
            ).exclude(id=self.instance.id).exists()
            if existe:
                raise forms.ValidationError("Este Código já está em uso nesta empresa.")
        return codigo

# --- NOVO: FORMULÁRIO DE FORMAS DE PAGAMENTO ---
class FormaPagamentoForm(forms.ModelForm):
    class Meta:
        model = FormaPagamento
        fields = ['nome', 'tipo', 'ativo']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'w-full bg-white border-2 border-slate-200 p-3 rounded-xl focus:border-blue-500 outline-none transition-all'
            })

# --- FORMULÁRIO DE CONTA (A PAGAR / RECEBER) ---
class ContaForm(forms.ModelForm):
    class Meta:
        model = Conta
        fields = [
            'descricao', 'plano_de_contas', 'cadastro', 'valor', 
            'data_vencimento', 'status', 'documento', 'observacoes', 'arquivo'
        ]
        widgets = {
            'data_vencimento': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
            'observacoes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        tipo_filtro = kwargs.pop('tipo_filtro', None)
        super().__init__(*args, **kwargs)
        
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'w-full bg-white border-2 border-slate-200 p-3 rounded-xl focus:border-blue-500 outline-none transition-all'
            })
            
        if user:
            # Filtra apenas cadastros deste Hotel (Hóspedes, Fornecedores ou Empresas Convênio)
            self.fields['cadastro'].queryset = Cadastro.objects.filter(empresa=user.empresa)
            planos = PlanoDeContas.objects.filter(empresa=user.empresa)
            if tipo_filtro:
                planos = planos.filter(tipo=tipo_filtro)
            self.fields['plano_de_contas'].queryset = planos

# --- FORMULÁRIO DE LANÇAMENTO MANUAL (FLUXO DE CAIXA) ---
class LancamentoManualForm(forms.ModelForm):
    class Meta:
        model = Lancamento
        fields = ['caixa', 'data_lancamento', 'tipo', 'plano_de_contas', 'descricao', 'valor']
        widgets = {
            'data_lancamento': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'w-full bg-white border-2 border-slate-200 p-3 rounded-xl focus:border-blue-500 outline-none transition-all'
            })
        
        if user:
            self.fields['caixa'].queryset = Caixa.objects.filter(empresa=user.empresa)
            self.fields['plano_de_contas'].queryset = PlanoDeContas.objects.filter(empresa=user.empresa)