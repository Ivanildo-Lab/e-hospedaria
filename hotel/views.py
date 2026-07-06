from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from decimal import Decimal
from datetime import timedelta

from core.models import ParametroSistema
from .models import ConsumoHospedagem, Quarto, CategoriaQuarto, Hospedagem
from .forms import CheckInForm, CategoriaQuartoForm, QuartoForm, FaixaPrecoFormSet
# Importando os modelos das outras APPS
from estoque.models import Produto, EstoqueFrigobar
from financeiro.models import Conta, Lancamento, PlanoDeContas, Caixa, FormaPagamento 

def home(request):
    return render(request, 'home.html')

@login_required
def mapa_quartos(request):
    quartos = Quarto.objects.filter(empresa=request.user.empresa).order_by('numero')
    produtos = Produto.objects.filter(empresa=request.user.empresa).order_by('nome')
    caixas = Caixa.objects.filter(empresa=request.user.empresa)
    formas_pagamento = FormaPagamento.objects.filter(empresa=request.user.empresa, ativo=True)
    
    return render(request, 'hotel/mapa_quartos.html', {
        'quartos': quartos,
        'produtos': produtos,
        'caixas': caixas,
        'formas_pagamento': formas_pagamento
    })

# --- GESTÃO DE CONFIGURAÇÕES (CATEGORIAS E QUARTOS) ---

@login_required
def lista_categorias(request):
    categorias = CategoriaQuarto.objects.filter(empresa=request.user.empresa)
    return render(request, 'hotel/categoria_lista.html', {'categorias': categorias})

@login_required
def nova_categoria(request):
    if request.method == 'POST':
        form = CategoriaQuartoForm(request.POST)
        formset = FaixaPrecoFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            cat = form.save(commit=False)
            cat.empresa = request.user.empresa
            cat.save()
            formset.instance = cat
            for f in formset.save(commit=False):
                f.empresa = request.user.empresa
                f.save()
            formset.save_m2m()
            messages.success(request, "Categoria criada com sucesso!")
            return redirect('hotel:lista_categorias')
    else:
        form = CategoriaQuartoForm()
        formset = FaixaPrecoFormSet()
    return render(request, 'hotel/form_categoria.html', {
        'form': form, 'formset': formset, 'titulo': 'Nova Categoria', 'editando': False
    })

@login_required
def editar_categoria(request, categoria_id):
    cat = get_object_or_404(CategoriaQuarto, id=categoria_id, empresa=request.user.empresa)
    if request.method == 'POST':
        form = CategoriaQuartoForm(request.POST, instance=cat)
        formset = FaixaPrecoFormSet(request.POST, instance=cat)
        if form.is_valid() and formset.is_valid():
            form.save()
            for f in formset.save(commit=False):
                f.empresa = request.user.empresa
                f.save()
            formset.save_m2m()
            messages.success(request, "Categoria atualizada com sucesso!")
            return redirect('hotel:lista_categorias')
    else:
        form = CategoriaQuartoForm(instance=cat)
        formset = FaixaPrecoFormSet(instance=cat)
    return render(request, 'hotel/form_categoria.html', {
        'form': form, 'formset': formset, 'titulo': f'Editar: {cat.nome}', 'editando': True
    })

@login_required
def excluir_categoria(request, categoria_id):
    cat = get_object_or_404(CategoriaQuarto, id=categoria_id, empresa=request.user.empresa)
    if request.method == 'POST':
        if cat.quarto_set.exists():
            messages.error(request, "Não é possível excluir uma categoria vinculada a quartos!")
        else:
            cat.delete()
            messages.success(request, "Categoria excluída!")
    return redirect('hotel:lista_categorias')

@login_required
def lista_quartos(request):
    quartos = Quarto.objects.filter(empresa=request.user.empresa).order_by('numero')
    return render(request, 'hotel/quarto_lista.html', {'quartos': quartos})

@login_required
def novo_quarto(request):
    if request.method == 'POST':
        form = QuartoForm(request.POST, user=request.user)
        if form.is_valid():
            quarto = form.save(commit=False)
            quarto.empresa = request.user.empresa
            quarto.save()
            messages.success(request, "Quarto cadastrado!")
            return redirect('hotel:lista_quartos')
    else:
        form = QuartoForm(user=request.user)
    return render(request, 'hotel/form_config.html', {'form': form, 'titulo': 'Novo Quarto'})

@login_required
def editar_quarto(request, quarto_id):
    quarto = get_object_or_404(Quarto, id=quarto_id, empresa=request.user.empresa)
    if request.method == 'POST':
        form = QuartoForm(request.POST, instance=quarto, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Quarto atualizado!")
            return redirect('hotel:lista_quartos')
    else:
        form = QuartoForm(instance=quarto, user=request.user)
    return render(request, 'hotel/form_config.html', {'form': form, 'titulo': f'Editar Quarto {quarto.numero}'})

@login_required
def excluir_quarto(request, quarto_id):
    quarto = get_object_or_404(Quarto, id=quarto_id, empresa=request.user.empresa)
    if request.method == 'POST':
        if quarto.status == 'OCUPADO':
            messages.error(request, "Não é possível excluir um quarto ocupado!")
        else:
            quarto.delete()
            messages.success(request, "Quarto excluído!")
    return redirect('hotel:lista_quartos')

# --- OPERACIONAL (CHECK-IN E LIMPEZA) ---

@login_required
def realizar_checkin(request, quarto_id):
    quarto = get_object_or_404(Quarto, id=quarto_id, empresa=request.user.empresa)
    faixas = quarto.categoria.faixas.all()
    if request.method == 'POST':
        form = CheckInForm(request.POST, user=request.user)
        if form.is_valid():
            hospedagem = form.save(commit=False)
            hospedagem.empresa = request.user.empresa
            hospedagem.quarto = quarto
            qtd = hospedagem.quantidade_hospedes
            hospedagem.valor_diaria_aplicada = quarto.categoria.preco_por_hospedes(qtd, hospedagem.tipo)
            hospedagem.save()
            quarto.status = 'OCUPADO'
            quarto.save()
            messages.success(request, "Check-in realizado!")
            return redirect('hotel:mapa_quartos')
    else:
        form = CheckInForm(user=request.user)
    return render(request, 'hotel/checkin_form.html', {
        'form': form, 'quarto': quarto, 'faixas': faixas
    })

@login_required
def liberar_limpeza(request, quarto_id):
    quarto = get_object_or_404(Quarto, id=quarto_id, empresa=request.user.empresa)
    if quarto.status == 'LIMPEZA':
        quarto.status = 'DISPONIVEL'
        quarto.save()
        messages.success(request, "Quarto liberado!")
    return redirect('hotel:mapa_quartos')

# --- O CORAÇÃO DO SISTEMA: CHECK-OUT COMPLETO ---

@login_required
def realizar_checkout(request, hospedagem_id):
    hospedagem = get_object_or_404(Hospedagem, id=hospedagem_id, empresa=request.user.empresa, ativa=True)
    quarto = hospedagem.quarto

    if request.method == 'POST':
        try:
            with transaction.atomic():
                # 1. CÁLCULO DA ESTADIA
                data_saida = timezone.now()
                duracao = data_saida - hospedagem.data_entrada
                
                if hospedagem.tipo == 'HORA':
                    horas = Decimal(duracao.total_seconds() / 3600)
                    if horas < 1: horas = Decimal('1')
                    hospedagem.valor_estadia = horas * hospedagem.valor_diaria_aplicada
                else:
                    dias = Decimal(duracao.days)
                    if dias < 1: dias = Decimal('1')
                    hospedagem.valor_estadia = dias * hospedagem.valor_diaria_aplicada

                # 2. PROCESSAMENTO DE CONSUMO E ESTOQUE
                ids_produtos = request.POST.getlist('produtos[]')
                qtds_produtos = request.POST.getlist('quantidades[]')
                total_c = Decimal('0.00')

                for p_id, qtd_str in zip(ids_produtos, qtds_produtos):
                    prod = get_object_or_404(Produto, id=p_id, empresa=request.user.empresa)
                    
                    # CORREÇÃO DO ERRO: Converter quantidade de texto para INTEIRO
                    quantidade_int = int(qtd_str) 

                    if quantidade_int > 0:
                        ConsumoHospedagem.objects.create(
                            empresa=request.user.empresa,
                            hospedagem=hospedagem,
                            produto=prod,
                            quantidade=quantidade_int, # Passando como Inteiro
                            valor_unitario=prod.preco_venda
                        )
                        total_c += (prod.preco_venda * Decimal(quantidade_int))
                        
                        if prod.tipo == 'P':
                            est = EstoqueFrigobar.objects.filter(quarto=quarto, produto=prod).first()
                            if est:
                                est.quantidade_atual -= quantidade_int
                                est.save()

                hospedagem.valor_consumo = total_c
                hospedagem.valor_total = hospedagem.valor_estadia + total_c
                hospedagem.data_saida = data_saida
                hospedagem.ativa = False
                
                # Pagador (Hóspede ou Convênio)
                pagador = hospedagem.hospede.empresa_convenio if hospedagem.hospede.empresa_convenio else hospedagem.hospede
                hospedagem.pagador_final = pagador
                hospedagem.save()
                
                # Libera o Quarto
                quarto.status = 'LIMPEZA'
                quarto.save()

                # 3. FINANCEIRO (Plano de Contas e Caixa)
                plano_r, _ = PlanoDeContas.objects.get_or_create(
                    empresa=request.user.empresa, 
                    nome="RECEITA DE HOSPEDAGEM", 
                    tipo='R', 
                    defaults={'codigo':'1.01'}
                )
                
                caixa_id = request.POST.get('caixa_id')
                caixa_sel = Caixa.objects.filter(id=caixa_id, empresa=request.user.empresa).first()
                
                # Se não selecionou caixa no modal, tenta o padrão
                if not caixa_sel:
                    param = ParametroSistema.objects.filter(empresa=request.user.empresa, chave='CAIXA_PADRAO_ID').first()
                    if param:
                        caixa_sel = Caixa.objects.filter(id=param.valor, empresa=request.user.empresa).first()

                # 4. PROCESSAR PAGAMENTOS MÚLTIPLOS (SPLIT)
                pgto_ids = request.POST.getlist('pgto_ids[]')
                pgto_valores = request.POST.getlist('pgto_valores[]')
                pgto_parcelas = request.POST.getlist('pgto_parcelas[]')

                for f_id, f_val_str, f_parc_str in zip(pgto_ids, pgto_valores, pgto_parcelas):
                    forma = get_object_or_404(FormaPagamento, id=f_id, empresa=request.user.empresa)
                    
                    # CONVERSÕES DE SEGURANÇA
                    v_fatia = Decimal(f_val_str)
                    n_parc = int(f_parc_str) if f_parc_str else 1

                    if forma.tipo == 'V': # À VISTA
                        ct = Conta.objects.create(
                            empresa=request.user.empresa,
                            descricao=f"Pgto {forma.nome} Q-{quarto.numero}",
                            plano_de_contas=plano_r,
                            cadastro=pagador,
                            valor=v_fatia,
                            data_vencimento=data_saida.date(),
                            status='PAGA',
                            documento=f"FAT-{hospedagem.id}"
                        )
                        if caixa_sel:
                            Lancamento.objects.create(
                                empresa=request.user.empresa,
                                caixa=caixa_sel,
                                plano_de_contas=plano_r,
                                conta_origem=ct,
                                data_lancamento=data_saida.date(),
                                valor=v_fatia,
                                tipo='C',
                                descricao=f"Receb. {forma.nome} Q-{quarto.numero}"
                            )
                    else: # A PRAZO (PARCELADO)
                        v_parc = v_fatia / Decimal(n_parc) # Divisão entre Decimais
                        for i in range(n_parc):
                            Conta.objects.create(
                                empresa=request.user.empresa,
                                descricao=f"Parc {i+1}/{n_parc} {forma.nome} Q-{quarto.numero}",
                                plano_de_contas=plano_r,
                                cadastro=pagador,
                                valor=v_parc,
                                data_vencimento=data_saida.date() + timedelta(days=30*i),
                                status='PENDENTE',
                                documento=f"FAT-{hospedagem.id}"
                            )

            messages.success(request, "Check-out e Financeiro processados com sucesso!")
            return redirect('hotel:imprimir_comprovante', hospedagem_id=hospedagem.id)

        except Exception as e:
            # Captura qualquer erro e mostra na tela para facilitar o debug
            messages.error(request, f"Erro operacional no fechamento: {str(e)}")
            return redirect('hotel:mapa_quartos')

    return redirect('hotel:mapa_quartos')
        
@login_required
def imprimir_comprovante(request, hospedagem_id):
    hospedagem = get_object_or_404(Hospedagem, id=hospedagem_id, empresa=request.user.empresa)
    consumos = hospedagem.consumos.all()
    # Busca todas as contas geradas por este checkout
    pagamentos = Conta.objects.filter(empresa=request.user.empresa, documento=f"FAT-{hospedagem.id}")
    
    return render(request, 'hotel/comprovante.html', {
        'hospedagem': hospedagem,
        'consumos': consumos,
        'pagamentos': pagamentos,
        'empresa': request.user.empresa
    })
# hotel/views.py

@login_required
def historico_hospedagens(request):
    # Busca apenas hospedagens ENCERRADAS (ativa=False)
    queryset = Hospedagem.objects.filter(empresa=request.user.empresa, ativa=False).order_by('-data_saida')

    # Filtro de busca (Nome do hóspede ou Número do Quarto)
    q = request.GET.get('q')
    if q:
        from django.db.models import Q
        queryset = queryset.filter(Q(hospede__nome__icontains=q) | Q(quarto__numero__icontains=q))

    return render(request, 'hotel/historico_lista.html', {'historico': queryset, 'filtro_q': q})
