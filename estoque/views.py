# estoque/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import F, Q
from django.db import transaction
from django.http import JsonResponse, HttpResponse
from .models import Produto, MovimentacaoEstoque, EstoqueFrigobar
from .forms import ProdutoForm, MovimentacaoForm
from datetime import timedelta
from financeiro.models import Conta, Lancamento, PlanoDeContas


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
            try:
                with transaction.atomic():
                    m = form.save(commit=False)
                    m.empresa = request.user.empresa
                    m.save()

                    if m.tipo == 'E' and m.fornecedor:
                        plano, created = PlanoDeContas.objects.get_or_create(
                            empresa=request.user.empresa,
                            nome="COMPRA DE MERCADORIAS / ESTOQUE",
                            tipo='D',
                            defaults={'codigo': '2.01'}
                        )

                        total_compra = m.quantidade * m.valor_unitario

                        if m.forma_pagamento == 'V':
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
                        else:
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
                messages.error(request, f"Erro ao processar financeiro: {str(e)}")
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


@login_required
def buscar_produtos(request):
    q = request.GET.get('q', '').strip()
    if len(q) < 2:
        return JsonResponse([], safe=False)
    produtos = Produto.objects.filter(
        empresa=request.user.empresa, tipo='P'
    ).filter(
        Q(nome__icontains=q) | Q(descricao__icontains=q)
    ).order_by('nome')[:20]
    data = [{'id': p.id, 'nome': p.nome, 'estoque': p.estoque_deposito, 'custo': str(p.valor_custo)} for p in produtos]
    return JsonResponse(data, safe=False)


@login_required
def buscar_fornecedores(request):
    q = request.GET.get('q', '').strip()
    if len(q) < 2:
        return JsonResponse([], safe=False)
    from cadastros.models import Cadastro
    fornecedores = Cadastro.objects.filter(
        empresa=request.user.empresa, papel__in=['FORNECEDOR', 'AMBOS'],
        nome__icontains=q
    ).order_by('nome')[:20]
    data = [{'id': f.id, 'nome': f.nome} for f in fornecedores]
    return JsonResponse(data, safe=False)


@login_required
def relatorio_estoque_pdf(request):
    from weasyprint import HTML

    produtos = Produto.objects.filter(
        empresa=request.user.empresa, tipo='P'
    ).order_by('nome')

    total_itens = 0
    valor_total_estoque = 0
    for p in produtos:
        p.valor_total_item = p.estoque_deposito * p.valor_custo
        p.status_estoque = 'CRITICO' if p.estoque_deposito <= 0 else 'BAIXO' if p.estoque_deposito <= p.estoque_minimo else 'OK'
        total_itens += p.estoque_deposito
        valor_total_estoque += p.valor_total_item

    html_string = render(request, 'estoque/relatorio_estoque_pdf.html', {
        'produtos': produtos,
        'empresa': request.user.empresa,
        'total_itens': total_itens,
        'valor_total_estoque': valor_total_estoque,
    }).content.decode('utf-8')

    pdf = HTML(string=html_string).write_pdf()
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="estoque_atual.pdf"'
    return response
