# cadastros/models.py
from django.db import models
from core.models import ModeloSaaS

class CategoriaCadastro(ModeloSaaS):
    nome = models.CharField(max_length=100)
    def __str__(self): return self.nome

class Cadastro(ModeloSaaS):
    TIPO_PESSOA_CHOICES = [('PF', 'Pessoa Física'), ('PJ', 'Pessoa Jurídica')]
    SITUACAO_CHOICES = [('ATIVO', 'Ativo'), ('INATIVO', 'Inativo')]
    PAPEL_CHOICES = [
        ('HOSPEDE', 'Hóspede'), 
        ('FORNECEDOR', 'Fornecedor'), 
        ('CONVENIO', 'Empresa/Convênio (Faturamento)'),
        ('AMBOS', 'Hóspede e Fornecedor')
    ]

    situacao = models.CharField(max_length=10, choices=SITUACAO_CHOICES, default='ATIVO')
    papel = models.CharField(max_length=15, choices=PAPEL_CHOICES, default='HOSPEDE')
    tipo_pessoa = models.CharField(max_length=2, choices=TIPO_PESSOA_CHOICES, default='PF')
    categoria = models.ForeignKey(CategoriaCadastro, on_delete=models.SET_NULL, null=True, blank=True)

    # Identificação
    nome = models.CharField(max_length=255, verbose_name="Nome Completo / Razão Social")
    cpf = models.CharField(max_length=14, blank=True, null=True, verbose_name="CPF")
    cnpj = models.CharField(max_length=18, blank=True, null=True, verbose_name="CNPJ")
    rg = models.CharField(max_length=20, blank=True, null=True, verbose_name="RG / Inscrição")
    
    # FNRH e Hotelaria
    data_nascimento = models.DateField(blank=True, null=True)
    profissao = models.CharField(max_length=100, blank=True, null=True)
    nacionalidade = models.CharField(max_length=100, default='Brasileira', blank=True)
    passaporte = models.CharField(max_length=50, blank=True, null=True)
    genero = models.CharField(max_length=20, choices=[('M', 'Masculino'), ('F', 'Feminino'), ('O', 'Outro')], blank=True, null=True)

    # Convênio
    empresa_convenio = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        limit_choices_to={'papel': 'CONVENIO'},
        related_name='hospedes_vinculados'
    )

    # Contato
    email = models.EmailField(blank=True, null=True)
    celular = models.CharField(max_length=20, blank=True, null=True)
    telefone_fixo = models.CharField(max_length=20, blank=True, null=True)

    # Endereço
    cep = models.CharField(max_length=10, blank=True, null=True)
    logradouro = models.CharField(max_length=255, blank=True, null=True)
    numero = models.CharField(max_length=20, blank=True, null=True)
    complemento = models.CharField(max_length=100, blank=True, null=True)
    bairro = models.CharField(max_length=100, blank=True, null=True)
    cidade = models.CharField(max_length=100, blank=True, null=True)
    uf = models.CharField(max_length=2, blank=True, null=True)
    
    observacoes = models.TextField(blank=True, null=True)

    def __str__(self): return self.nome