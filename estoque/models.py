from django.db import models
from core.models import ModeloSaaS

class Produto(ModeloSaaS):
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True, null=True)
    
    # Valores
    valor_custo = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    preco_venda = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Estoque no Depósito Principal
    estoque_deposito = models.IntegerField(default=0, verbose_name="Qtd no Depósito")
    estoque_minimo = models.IntegerField(default=5)

    def __str__(self):
        return self.nome

class EstoqueFrigobar(ModeloSaaS):
    """
    Controla o que existe dentro de cada quarto.
    Isso permite o relatório de reposição automática.
    """
    quarto = models.ForeignKey('hotel.Quarto', on_delete=models.CASCADE, related_name='frigobar')
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    quantidade_atual = models.IntegerField(default=0)
    capacidade_maxima = models.IntegerField(default=5, help_text="Qtd máxima que cabe no frigobar")

    class Meta:
        unique_together = ['quarto', 'produto']
        verbose_name = "Estoque do Frigobar"
        verbose_name_plural = "Estoques dos Frigobares"

    def __str__(self):
        return f"{self.produto.nome} - Quarto {self.quarto.numero}"

class MovimentacaoEstoque(ModeloSaaS):
    TIPO_MOV = [('E', 'Entrada (Compra)'), ('S', 'Saída (Perda/Ajuste)')]
    
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    quantidade = models.IntegerField()
    tipo = models.CharField(max_length=1, choices=TIPO_MOV)
    data = models.DateTimeField(auto_now_add=True)
    observacao = models.CharField(max_length=255, blank=True)

    def save(self, *args, **kwargs):
        # Atualiza o estoque do depósito ao salvar uma movimentação manual
        if not self.pk:
            if self.tipo == 'E':
                self.produto.estoque_deposito += self.quantidade
            else:
                self.produto.estoque_deposito -= self.quantidade
            self.produto.save()
        super().save(*args, **kwargs)