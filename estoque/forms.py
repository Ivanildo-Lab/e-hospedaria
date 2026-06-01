# estoque/forms.py
from django import forms
from .models import Produto, MovimentacaoEstoque

class ProdutoForm(forms.ModelForm): # <--- Corrigido aqui
    class Meta:
        model = Produto
        fields = ['nome', 'valor_custo', 'preco_venda', 'estoque_minimo']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'w-full border-2 border-slate-100 p-3 rounded-xl focus:border-blue-500 outline-none transition-all'})

class MovimentacaoForm(forms.ModelForm):
    class Meta:
        model = MovimentacaoEstoque
        fields = ['produto', 'quantidade', 'tipo', 'observacao']
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['produto'].queryset = Produto.objects.filter(empresa=user.empresa)
        
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'w-full border-2 border-slate-100 p-3 rounded-xl focus:border-blue-500 outline-none transition-all'})