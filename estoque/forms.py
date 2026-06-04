from django import forms
from .models import Produto, MovimentacaoEstoque

class ProdutoForm(forms.ModelForm):
    class Meta:
        model = Produto
        fields = ['tipo', 'nome', 'valor_custo', 'preco_venda', 'estoque_minimo']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'w-full bg-white border-2 border-slate-200 p-3 rounded-xl focus:border-blue-500 outline-none transition-all'})

# estoque/forms.py
from django import forms
from .models import MovimentacaoEstoque, Produto
from cadastros.models import Cadastro
from financeiro.models import Caixa

class MovimentacaoForm(forms.ModelForm):
    # Campo extra que não está no banco, mas usamos para a lógica de pagamento à vista
    caixa_pagamento = forms.ModelChoiceField(
        queryset=Caixa.objects.none(), 
        required=False, 
        label="Sair dinheiro de qual Caixa?"
    )

    class Meta:
        model = MovimentacaoEstoque
        fields = [
            'produto', 'fornecedor', 'quantidade', 'valor_unitario', 
            'tipo', 'forma_pagamento', 'num_parcelas', 'observacao'
        ]

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            self.fields['produto'].queryset = Produto.objects.filter(empresa=user.empresa, tipo='P')
            self.fields['fornecedor'].queryset = Cadastro.objects.filter(empresa=user.empresa, papel__in=['FORNECEDOR', 'AMBOS'])
            self.fields['caixa_pagamento'].queryset = Caixa.objects.filter(empresa=user.empresa)

        # Aplicando a classe Tailwind em todos os campos
        for field_name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'w-full bg-white border-2 border-slate-200 p-3 rounded-xl focus:border-blue-500 outline-none transition-all'
            })