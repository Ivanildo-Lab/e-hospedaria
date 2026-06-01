# cadastros/forms.py
from django import forms
from .models import Cadastro, CategoriaCadastro

class CadastroForm(forms.ModelForm):
    data_nascimento = forms.DateField(
        label="Data de Nascimento",
        required=False,
        widget=forms.DateInput(
            format='%d/%m/%Y', # Formato brasileiro
            attrs={
                'placeholder': 'dd/mm/aaaa',
                'class': 'mask-data' # Classe para o Javascript encontrar
            }
        ),
        input_formats=['%d/%m/%Y', '%Y-%m-%d'] # Formatos que o Django vai aceitar no POST
    )

    class Meta:
        model = Cadastro
        fields = [
            'nome', 'tipo_pessoa', 'cpf', 'cnpj', 'rg', 'data_nascimento',
            'profissao', 'nacionalidade', 'passaporte', 'genero',
            'empresa_convenio', 'papel', 'categoria', 'email', 'celular',
            'telefone_fixo', 'cep', 'logradouro', 'numero', 'complemento',
            'bairro', 'cidade', 'uf', 'observacoes'
        ]
        widgets = {
            'observacoes': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Dicionário de ajuda para os campos
        placeholders = {
            'email': 'exemplo@email.com',
            'celular': '(00) 90000-0000',
            'telefone_fixo': '(00) 0000-0000',
            'cep': '00000-000',
            'logradouro': 'Rua, Avenida, etc...',
            'numero': 'Nº',
            'bairro': 'Bairro',
            'cidade': 'Cidade',
            'uf': 'UF',
        }

        if user:
            self.fields['categoria'].queryset = CategoriaCadastro.objects.filter(empresa=user.empresa)
            self.fields['empresa_convenio'].queryset = Cadastro.objects.filter(
                empresa=user.empresa, papel='CONVENIO'
            )

        for field_name, field in self.fields.items():
            # Adiciona a classe visual e o placeholder
            field.widget.attrs.update({
                'class': 'w-full bg-white border-2 border-slate-200 p-3 rounded-xl focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 outline-none transition-all text-slate-700 font-medium',
                'placeholder': placeholders.get(field_name, '')
            })