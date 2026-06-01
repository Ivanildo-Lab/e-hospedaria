from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Produto, MovimentacaoEstoque, EstoqueFrigobar
from .forms import ProdutoForm, MovimentacaoForm

@login_required
def lista_produtos(request):
    produtos = Produto.objects.filter(empresa=request.user.empresa)
    return render(request, 'estoque/lista_produtos.html', {'produtos': produtos})

@login_required
def entrada_estoque(request):
    """View para entrada de notas/compras"""
    if request.method == 'POST':
        form = MovimentacaoForm(request.POST, user=request.user)
        if form.is_valid():
            mov = form.save(commit=False)
            mov.empresa = request.user.empresa
            mov.save() # O save() do modelo já atualiza o saldo do depósito
            messages.success(request, "Movimentação registrada com sucesso!")
            return redirect('estoque:lista_produtos')
    else:
        form = MovimentacaoForm(user=request.user, initial={'tipo': 'E'})
    return render(request, 'estoque/form_movimentacao.html', {'form': form})

# estoque/views.py
from django.db.models import F

@login_required
def relatorio_reposicao(request):
    """Relatório que mostra o que precisa ser reposto nos quartos"""
    itens = EstoqueFrigobar.objects.filter(
        empresa=request.user.empresa,
        quantidade_atual__lt=F('capacidade_maxima')
    ).select_related('quarto', 'produto')
    
    # Adicionamos um atributo dinâmico 'necessidade' em cada item
    for item in itens:
        item.necessidade = item.capacidade_maxima - item.quantidade_atual
    
    return render(request, 'estoque/relatorio_reposicao.html', {'itens': itens})