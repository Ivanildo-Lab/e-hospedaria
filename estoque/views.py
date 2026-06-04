# estoque/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import F
from .models import Produto, MovimentacaoEstoque, EstoqueFrigobar
from .forms import ProdutoForm, MovimentacaoForm
from datetime import timedelta


@login_required
def lista_produtos(request):
    tipo_filtro = request.GET.get('tipo')
    produtos = Produto.objects.filter(empresa=request.user.empresa).order_by('nome')
    if tipo_filtro:
        produtos = produtos.filter(tipo=tipo_filtro)
    return render(request, 'estoque/lista_produtos.html', {'produtos': produtos, 'filtro': tipo_filtro})

@login_required
def novo_produto(request):
    if request.method == 'POST':
        form = ProdutoForm(request.POST)
        if form.is_valid():
            p = form.save(commit=False)
            p.empresa = request.user.empresa
            p.save()
            messages.success(request, f"Item '{p.nome}' cadastrado!")
            return redirect('estoque:lista_produtos')
    else:
        form = ProdutoForm()
    return render(request, 'estoque/form_produto.html', {'form': form, 'titulo': 'Novo Item (Produto/Serviço)'})

@login_required
def editar_produto(request, pk):
    produto = get_object_or_404(Produto, pk=pk, empresa=request.user.empresa)
    if request.method == 'POST':
        form = ProdutoForm(request.POST, instance=produto)
        if form.is_valid():
            form.save()
            messages.success(request, "Item atualizado!")
            return redirect('estoque:lista_produtos')
    else:
        form = ProdutoForm(instance=produto)
    return render(request, 'estoque/form_produto.html', {'form': form, 'titulo': 'Editar Item'})

@login_required
def registrar_movimentacao(request):
    if request.method == 'POST':
        form = MovimentacaoForm(request.POST, user=request.user)
        if form.is_valid():
            m = form.save(commit=False)
            m.empresa = request.user.empresa
            m.save()
            messages.success(request, "Movimentação de estoque registrada!")
            return redirect('estoque:lista_produtos')
    else:
        form = MovimentacaoForm(user=request.user)
    return render(request, 'estoque/form_movimentacao.html', {'form': form})

@login_required
def relatorio_reposicao(request):
    itens = EstoqueFrigobar.objects.filter(
        empresa=request.user.empresa,
        quantidade_atual__lt=F('capacidade_maxima')
    ).select_related('quarto', 'produto')
    
    for item in itens:
        item.necessidade = item.capacidade_maxima - item.quantidade_atual
        
    return render(request, 'estoque/relatorio_reposicao.html', {'itens': itens})

# estoque/views.py
from datetime import timedelta
from financeiro.models import Conta, Lancamento, PlanoDeContas

# estoque/views.py
from datetime import timedelta
from financeiro.models import Conta, Lancamento, PlanoDeContas
from django.db import transaction # Para garantir que salve tudo ou nada

@login_required
def registrar_movimentacao(request):
    if request.method == 'POST':
        form = MovimentacaoForm(request.POST, user=request.user)
        if form.is_valid():
            try:
                with transaction.atomic(): # Segurança para o banco de dados
                    m = form.save(commit=False)
                    m.empresa = request.user.empresa
                    m.save() 

                    # SÓ INTEGRA SE FOR ENTRADA (COMPRA)
                    if m.tipo == 'E' and m.fornecedor:
                        # --- LÓGICA DO PLANO DE CONTAS PADRÃO ---
                        # Busca ou cria a categoria para evitar o erro de 'Column cannot be null'
                        plano, created = PlanoDeContas.objects.get_or_create(
                            empresa=request.user.empresa,
                            nome="COMPRA DE MERCADORIAS / ESTOQUE",
                            tipo='D', # Despesa
                            defaults={'codigo': '2.01'}
                        )

                        total_compra = m.quantidade * m.valor_unitario

                        if m.forma_pagamento == 'V': # À VISTA
                            caixa = form.cleaned_data.get('caixa_pagamento')
                            if not caixa:
                                messages.error(request, "Para compras à vista, selecione o caixa de saída.")
                                raise Exception("Caixa não selecionado")

                            Lancamento.objects.create(
                                empresa=request.user.empresa,
                                caixa=caixa,
                                plano_de_contas=plano,
                                data_lancamento=m.data.date(),
                                descricao=f"Compra Estq: {m.quantidade}x {m.produto.nome}",
                                valor=total_compra,
                                tipo='D'
                            )
                        
                        else: # A PRAZO (PARCELADO)
                            qtd_parcelas = m.num_parcelas or 1
                            valor_parcela = total_compra / qtd_parcelas
                            for i in range(qtd_parcelas):
                                Conta.objects.create(
                                    empresa=request.user.empresa,
                                    descricao=f"Parc {i+1}/{qtd_parcelas} - {m.produto.nome}",
                                    plano_de_contas=plano,
                                    cadastro=m.fornecedor,
                                    valor=valor_parcela,
                                    data_vencimento=m.data.date() + timedelta(days=30 * (i + 1)),
                                    status='PENDENTE',
                                    documento=f"MOV-{m.id}"
                                )

                messages.success(request, "Estoque e Financeiro atualizados com sucesso!")
                return redirect('estoque:lista_produtos')

            except Exception as e:
                # Se algo der errado na integração financeira, o estoque também não é alterado (atomic)
                messages.error(request, f"Erro ao processar financeiro: {str(e)}")
    else:
        form = MovimentacaoForm(user=request.user)
    
    return render(request, 'estoque/form_movimentacao.html', {'form': form})
