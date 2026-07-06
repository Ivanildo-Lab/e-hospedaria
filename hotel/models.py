from django.db import models
from core.models import ModeloSaaS
from cadastros.models import Cadastro
from django.utils import timezone

class CategoriaQuarto(ModeloSaaS):
    nome = models.CharField(max_length=100)
    preco_diaria = models.DecimalField(max_digits=10, decimal_places=2)
    preco_hora = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.nome

    def preco_por_hospedes(self, qtd, tipo='DIARIA'):
        faixa = self.faixas.filter(qtd_hospedes__lte=qtd).order_by('-qtd_hospedes').first()
        if faixa:
            return faixa.preco_diaria if tipo == 'DIARIA' else faixa.preco_hora
        return self.preco_diaria if tipo == 'DIARIA' else self.preco_hora


class FaixaPrecoCategoria(ModeloSaaS):
    categoria = models.ForeignKey(CategoriaQuarto, on_delete=models.CASCADE, related_name='faixas')
    qtd_hospedes = models.PositiveIntegerField()
    preco_diaria = models.DecimalField(max_digits=10, decimal_places=2)
    preco_hora = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        ordering = ['qtd_hospedes']

    def __str__(self):
        return f"{self.categoria.nome} - {self.qtd_hospedes} hóspede(s)"

class Quarto(ModeloSaaS):
    STATUS_CHOICES = [
        ('DISPONIVEL', 'Disponível'),
        ('OCUPADO', 'Ocupado'),
        ('LIMPEZA', 'Limpeza'),
        ('MANUTENCAO', 'Manutenção'),
    ]
    numero = models.CharField(max_length=10)
    categoria = models.ForeignKey(CategoriaQuarto, on_delete=models.PROTECT)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DISPONIVEL')

    def hospedagem_atual(self):
        return self.hospedagem_set.filter(ativa=True).first()
    
    def __str__(self):
        return f"Quarto {self.numero}"

class Hospedagem(ModeloSaaS):
    TIPO_CHOICES = [('DIARIA', 'Diária'), ('HORA', 'Hora')]
    
    quarto = models.ForeignKey(Quarto, on_delete=models.PROTECT)
    hospede = models.ForeignKey(Cadastro, on_delete=models.PROTECT, limit_choices_to={'papel': 'HOSPEDE'})
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES, default='DIARIA')
    quantidade_hospedes = models.PositiveIntegerField(default=1)
    valor_diaria_aplicada = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    data_entrada = models.DateTimeField(default=timezone.now)
    data_saida = models.DateTimeField(null=True, blank=True)
    ativa = models.BooleanField(default=True)
    valor_estadia = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    valor_consumo = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    valor_total = models.DecimalField(max_digits=10, decimal_places=2, default=0)    
    pagador_final = models.ForeignKey('cadastros.Cadastro', on_delete=models.SET_NULL, null=True, blank=True, related_name='contas_pagas')


    def save(self, *args, **kwargs):
        # Ao salvar um novo check-in, o quarto fica OCUPADO
        if not self.pk:
            self.quarto.status = 'OCUPADO'
            self.quarto.save()
        super().save(*args, **kwargs)

# hotel/models.py

class ConsumoHospedagem(ModeloSaaS):
    hospedagem = models.ForeignKey(Hospedagem, on_delete=models.CASCADE, related_name='consumos')
    produto = models.ForeignKey('estoque.Produto', on_delete=models.PROTECT)
    quantidade = models.IntegerField(default=1)
    valor_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        self.total = self.quantidade * self.valor_unitario
        super().save(*args, **kwargs)