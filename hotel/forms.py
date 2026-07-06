# hotel/forms.py
from django import forms
from .models import Hospedagem
from cadastros.models import Cadastro
from .models import CategoriaQuarto, Quarto, FaixaPrecoCategoria


class CheckInForm(forms.ModelForm):
    class Meta:
        model = Hospedagem
        fields = ['hospede', 'tipo', 'quantidade_hospedes']
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['hospede'].queryset = Cadastro.objects.filter(
                empresa=user.empresa, 
                papel__in=['HOSPEDE', 'AMBOS'],
                situacao='ATIVO'
            )
        
        self.fields['quantidade_hospedes'].widget = forms.NumberInput(attrs={
            'min': 1, 'max': 20, 'value': 1,
            'class': 'w-full border-2 border-slate-100 p-4 rounded-2xl focus:border-blue-500 outline-none transition-all'
        })

        for name, field in self.fields.items():
            if name != 'quantidade_hospedes':
                field.widget.attrs.update({'class': 'w-full border-2 border-slate-100 p-4 rounded-2xl focus:border-blue-500 outline-none transition-all'})


FaixaPrecoFormSet = forms.inlineformset_factory(
    CategoriaQuarto,
    FaixaPrecoCategoria,
    fields=['qtd_hospedes', 'preco_diaria', 'preco_hora'],
    extra=1,
    can_delete=True
)


class FaixaPrecoCategoriaForm(forms.ModelForm):
    class Meta:
        model = FaixaPrecoCategoria
        fields = ['qtd_hospedes', 'preco_diaria', 'preco_hora']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'w-full border-2 border-slate-100 p-3 rounded-xl focus:border-blue-500 outline-none transition-all text-sm'})


class CategoriaQuartoForm(forms.ModelForm):
    class Meta:
        model = CategoriaQuarto
        fields = ['nome', 'preco_diaria', 'preco_hora']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'w-full border-2 border-slate-100 p-3 rounded-xl focus:border-blue-500 outline-none transition-all'})

class QuartoForm(forms.ModelForm):
    class Meta:
        model = Quarto
        fields = ['numero', 'categoria', 'status']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['categoria'].queryset = CategoriaQuarto.objects.filter(empresa=user.empresa)
        
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'w-full border-2 border-slate-100 p-3 rounded-xl focus:border-blue-500 outline-none transition-all'})
        