from django.db import models
from core.models import ModeloSaaS

class Produto(ModeloSaaS):
    TIPO_CHOICES = [('P', 'Produto Físico'), ('S', 'Serviço')]
    
    tipo = models.CharField(max_length=1, choices=TIPO_CHOICES, default='P')
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True, null=True)
    
    # Valores
    valor_custo = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Valor de Custo")
    preco_venda = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Preço de Venda")
    
    # Estoque no Depósito Principal (Apenas para tipo 'P')
    estoque_deposito = models.IntegerField(default=0, verbose_name="Saldo no Depósito")
    estoque_minimo = models.IntegerField(default=5, verbose_name="Estoque Mínimo")

    def __str__(self):
        prefixo = "[SERV]" if self.tipo == 'S' else "[PROD]"
        return f"{prefixo} {self.nome}"

class EstoqueFrigobar(ModeloSaaS):
    """Controla a quantidade de produtos físicos em cada quarto"""
    quarto = models.ForeignKey('hotel.Quarto', on_delete=models.CASCADE, related_name='frigobar')
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, limit_choices_to={'tipo': 'P'})
    quantidade_atual = models.IntegerField(default=0)
    capacidade_maxima = models.IntegerField(default=5)

    class Meta:
        unique_together = ['quarto', 'produto']
        verbose_name = "Estoque do Frigobar"
        verbose_name_plural = "Estoques dos Frigobares"

    def __str__(self):
        return f"{self.produto.nome} - Quarto {self.quarto.numero}"

class MovimentacaoEstoque(ModeloSaaS):
    TIPO_MOV = [('E', 'Entrada (Compra/Ajuste)'), ('S', 'Saída (Perda/Ajuste)')]
    
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, limit_choices_to={'tipo': 'P'})
    quantidade = models.IntegerField()
    tipo = models.CharField(max_length=1, choices=TIPO_MOV)
    data = models.DateTimeField(auto_now_add=True)
    observacao = models.CharField(max_length=255, blank=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            if self.tipo == 'E':
                self.produto.estoque_deposito += self.quantidade
            else:
                self.produto.estoque_deposito -= self.quantidade
            self.produto.save()
        super().save(*args, **kwargs)

class Inventario(ModeloSaaS):
    """Snapshot para fechamento de estoque"""
    data_fechamento = models.DateTimeField(auto_now_add=True)
    responsavel = models.CharField(max_length=100)
    observacoes = models.TextField(blank=True)

    def __str__(self):
        return f"Inventário {self.data_fechamento.strftime('%d/%m/%Y')}"

class MovimentacaoEstoque(ModeloSaaS):
    TIPO_MOV = [('E', 'Entrada (Compra)'), ('S', 'Saída (Perda/Ajuste)')]
    FORMA_PAGAMENTO = [('V', 'À Vista (Caixa)'), ('P', 'A Prazo (Contas a Pagar)')]
    
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, limit_choices_to={'tipo': 'P'})
    quantidade = models.IntegerField()
    tipo = models.CharField(max_length=1, choices=TIPO_MOV)
    
    # NOVOS CAMPOS PARA INTEGRAÇÃO FINANCEIRA
    fornecedor = models.ForeignKey('cadastros.Cadastro', on_delete=models.PROTECT, null=True, blank=True, limit_choices_to={'papel__in': ['FORNECEDOR', 'AMBOS']})
    valor_unitario = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    forma_pagamento = models.CharField(max_length=1, choices=FORMA_PAGAMENTO, null=True, blank=True)
    num_parcelas = models.IntegerField(default=1, verbose_name="Número de Parcelas")    
    data = models.DateTimeField(auto_now_add=True)
    observacao = models.CharField(max_length=255, blank=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            if self.tipo == 'E':
                self.produto.estoque_deposito += self.quantidade
                # Atualiza o valor de custo do produto com base na última compra
                self.produto.valor_custo = self.valor_unitario
            else:
                self.produto.estoque_deposito -= self.quantidade
            self.produto.save()
        super().save(*args, **kwargs)