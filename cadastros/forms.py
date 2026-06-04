from django import forms
from .models import Cadastro, CategoriaCadastro

class CadastroForm(forms.ModelForm):
    # Definimos o campo de data manualmente para permitir a digitação livre com máscara JS
    data_nascimento = forms.DateField(
        label="Data de Nascimento / Fundação",
        required=False,
        widget=forms.DateInput(
            format='%d/%m/%Y',
            attrs={
                'placeholder': 'dd/mm/aaaa',
                'class': 'mask-data'
            }
        ),
        input_formats=['%d/%m/%Y', '%Y-%m-%d']
    )

    class Meta:
        model = Cadastro
        # Listagem de todos os campos na ordem desejada
        fields = [
            'nome', 'tipo_pessoa', 'papel', 'cpf', 'cnpj', 'rg', 'data_nascimento',
            'profissao', 'nacionalidade', 'passaporte', 'genero',
            'empresa_convenio', 'categoria', 'email', 'celular',
            'telefone_fixo', 'cep', 'logradouro', 'numero', 'complemento',
            'bairro', 'cidade', 'uf', 'observacoes'
        ]
        widgets = {
            'observacoes': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        # Captura as variáveis enviadas pela View
        self.user = kwargs.pop('user', None)
        self.fornecedor_mode = kwargs.pop('fornecedor_mode', False)
        
        super().__init__(*args, **kwargs)

        # 1. LÓGICA DE OTIMIZAÇÃO: MODO FORNECEDOR
        # Se for fornecedor, removemos os campos de Hóspede para limpar a tela
        if self.fornecedor_mode:
            campos_hospede = [
                'profissao', 'nacionalidade', 'passaporte', 
                'genero', 'empresa_convenio', 'categoria'
            ]
            for campo in campos_hospede:
                if campo in self.fields:
                    del self.fields[campo]
            
            # Fixa o papel como FORNECEDOR e esconde o campo
            if 'papel' in self.fields:
                self.fields['papel'].initial = 'FORNECEDOR'
                self.fields['papel'].widget = forms.HiddenInput()
            
            # Define Pessoa Jurídica como padrão para fornecedores
            if 'tipo_pessoa' in self.fields:
                self.fields['tipo_pessoa'].initial = 'PJ'

        # 2. FILTROS SAAS (Segurança por Empresa)
        if self.user and self.user.empresa:
            # Filtra categorias apenas deste hotel
            if 'categoria' in self.fields:
                self.fields['categoria'].queryset = CategoriaCadastro.objects.filter(empresa=self.user.empresa)
            
            # Filtra empresas de convênio apenas deste hotel
            if 'empresa_convenio' in self.fields:
                self.fields['empresa_convenio'].queryset = Cadastro.objects.filter(
                    empresa=self.user.empresa, 
                    papel='CONVENIO'
                ).exclude(id=self.instance.id) # Evita vincular uma empresa a ela mesma

        # 3. ESTILIZAÇÃO TAILWIND E PLACEHOLDERS
        placeholders = {
            'email': 'exemplo@email.com',
            'celular': '(00) 90000-0000',
            'telefone_fixo': '(00) 0000-0000',
            'cep': '00000-000',
            'cpf': '000.000.000-00',
            'cnpj': '00.000.000/0000-00',
            'rg': 'Número do RG ou Inscrição',
        }

        for field_name, field in self.fields.items():
            # Classe base visual
            css_classes = 'w-full bg-white border-2 border-slate-200 p-3 rounded-xl focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 outline-none transition-all text-slate-700 font-medium'
            
            # Adiciona classes específicas para as máscaras JS se necessário
            if field_name == 'cpf': css_classes += ' mask-cpf'
            if field_name == 'cnpj': css_classes += ' mask-cnpj'
            if field_name == 'cep': css_classes += ' mask-cep'
            
            field.widget.attrs.update({
                'class': css_classes,
                'placeholder': placeholders.get(field_name, '')
            })

    # VALIDAÇÃO DE CPF ÚNICO POR EMPRESA
    def clean_cpf(self):
        cpf = self.cleaned_data.get('cpf')
        if cpf and self.user:
            exists = Cadastro.objects.filter(
                empresa=self.user.empresa, 
                cpf=cpf
            ).exclude(id=self.instance.id).exists()
            if exists:
                raise forms.ValidationError("Este CPF já está cadastrado para outro hóspede neste hotel.")
        return cpf

    # VALIDAÇÃO DE CNPJ ÚNICO POR EMPRESA
    def clean_cnpj(self):
        cnpj = self.cleaned_data.get('cnpj')
        if cnpj and self.user:
            exists = Cadastro.objects.filter(
                empresa=self.user.empresa, 
                cnpj=cnpj
            ).exclude(id=self.instance.id).exists()
            if exists:
                raise forms.ValidationError("Este CNPJ já está cadastrado para outra empresa neste hotel.")
        return cnpj