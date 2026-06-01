# hotel/forms.py
from django import forms
from .models import Hospedagem
from cadastros.models import Cadastro
from .models import CategoriaQuarto, Quarto


class CheckInForm(forms.ModelForm):
    class Meta:
        model = Hospedagem
        fields = ['hospede', 'tipo']
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            # Mostra apenas hóspedes daquela empresa
            self.fields['hospede'].queryset = Cadastro.objects.filter(
                empresa=user.empresa, 
                papel__in=['HOSPEDE', 'AMBOS'],
                situacao='ATIVO'
            )
        
        # Estilização Tailwind
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'w-full border-2 border-slate-100 p-4 rounded-2xl focus:border-blue-500 outline-none transition-all'})


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
            # Filtra apenas as categorias criadas por este hotel
            self.fields['categoria'].queryset = CategoriaQuarto.objects.filter(empresa=user.empresa)
        
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'w-full border-2 border-slate-100 p-3 rounded-xl focus:border-blue-500 outline-none transition-all'})
        