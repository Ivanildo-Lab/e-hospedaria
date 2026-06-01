# hotel/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Quarto, CategoriaQuarto, Hospedagem
from .forms import CheckInForm, CategoriaQuartoForm, QuartoForm
from financeiro.models import Conta, PlanoDeContas # Importante para a integração
from decimal import Decimal
from django.utils import timezone
from django.http import JsonResponse
from estoque.models import Produto

def home(request):
    return render(request, 'home.html')

@login_required
def mapa_quartos(request):
    quartos = Quarto.objects.filter(empresa=request.user.empresa).order_by('numero')
    return render(request, 'hotel/mapa_quartos.html', {'quartos': quartos})

# --- GESTÃO DE CATEGORIAS ---
@login_required
def lista_categorias(request):
    categorias = CategoriaQuarto.objects.filter(empresa=request.user.empresa)
    return render(request, 'hotel/categoria_lista.html', {'categorias': categorias})

# hotel/views.py

@login_required
def nova_categoria(request):
    if request.method == 'POST':
        form = CategoriaQuartoForm(request.POST)
        if form.is_valid():
            # Verifica se o usuário tem uma empresa vinculada antes de salvar
            if not request.user.empresa:
                messages.error(request, "Erro: Seu usuário não está vinculado a nenhuma empresa. Procure o administrador.")
                return redirect('hotel:lista_categorias')

            cat = form.save(commit=False)
            cat.empresa = request.user.empresa  # Aqui injetamos a empresa
            cat.save()
            messages.success(request, "Categoria criada com sucesso!")
            return redirect('hotel:lista_categorias')
    else:
        form = CategoriaQuartoForm()
    return render(request, 'hotel/form_config.html', {'form': form, 'titulo': 'Nova Categoria'})


# --- GESTÃO DE QUARTOS ---
@login_required
def lista_quartos(request):
    quartos = Quarto.objects.filter(empresa=request.user.empresa).order_by('numero')
    return render(request, 'hotel/quarto_lista.html', {'quartos': quartos})

@login_required
def novo_quarto(request):
    if request.method == 'POST':
        form = QuartoForm(request.POST, user=request.user)
        if form.is_valid():
            # Proteção SaaS
            if not request.user.empresa:
                messages.error(request, "Erro: Seu usuário não está vinculado a nenhuma empresa.")
                return redirect('hotel:lista_quartos')

            quarto = form.save(commit=False)
            quarto.empresa = request.user.empresa
            quarto.save()
            messages.success(request, "Quarto cadastrado com sucesso!")
            return redirect('hotel:lista_quartos')
    else:
        form = QuartoForm(user=request.user)
    return render(request, 'hotel/form_config.html', {'form': form, 'titulo': 'Novo Quarto'})

# --- OPERACIONAL ---
@login_required
def realizar_checkin(request, quarto_id):
    quarto = get_object_or_404(Quarto, id=quarto_id, empresa=request.user.empresa)
    if request.method == 'POST':
        form = CheckInForm(request.POST, user=request.user)
        if form.is_valid():
            hospedagem = form.save(commit=False)
            hospedagem.empresa = request.user.empresa
            hospedagem.quarto = quarto
            hospedagem.save()
            quarto.status = 'OCUPADO'
            quarto.save()
            messages.success(request, f"Check-in realizado no Quarto {quarto.numero}!")
            return redirect('hotel:mapa_quartos')
    else:
        form = CheckInForm(user=request.user)
    return render(request, 'hotel/checkin_form.html', {'form': form, 'quarto': quarto})

@login_required
def liberar_limpeza(request, quarto_id):
    quarto = get_object_or_404(Quarto, id=quarto_id, empresa=request.user.empresa)
    if quarto.status == 'LIMPEZA':
        quarto.status = 'DISPONIVEL'
        quarto.save()
        messages.success(request, f"Quarto {quarto.numero} liberado!")
    return redirect('hotel:mapa_quartos')


@login_required
def realizar_checkout(request, hospedagem_id):
    hospedagem = get_object_or_404(Hospedagem, id=hospedagem_id, empresa=request.user.empresa, ativa=True)
    quarto = hospedagem.quarto

    if request.method == 'POST':
        # 1. Recebe os dados do formulário/modal
        data_saida = timezone.now()
        
        # 2. Processa o Consumo (Itens enviados via lista no POST)
        ids_produtos = request.POST.getlist('produtos[]')
        qtds_produtos = request.POST.getlist('quantidades[]')
        total_consumo = Decimal('0.00')

        for p_id, qtd in zip(ids_produtos, qtds_produtos):
            produto = get_object_or_404(Produto, id=p_id, empresa=request.user.empresa)
            quantidade = int(qtd)
            if quantidade > 0:
                ConsumoHospedagem.objects.create(
                    empresa=request.user.empresa,
                    hospedagem=hospedagem,
                    produto=produto,
                    quantidade=quantidade,
                    valor_unitario=produto.preco_venda
                )
                total_consumo += (produto.preco_venda * quantidade)
                # Opcional: Baixa no estoque aqui

        # 3. Cálculo da Estadia
        duracao = data_saida - hospedagem.data_entrada
        if hospedagem.tipo == 'HORA':
            horas = Decimal(duracao.total_seconds() / 3600)
            if horas < 1: horas = 1
            valor_estadia = horas * quarto.categoria.preco_hora
        else:
            dias = Decimal(duracao.days)
            if dias < 1: dias = 1
            valor_estadia = dias * quarto.categoria.preco_diaria

        # 4. Finalização
        hospedagem.valor_estadia = valor_estadia
        hospedagem.valor_consumo = total_consumo
        hospedagem.valor_total = valor_estadia + total_consumo
        hospedagem.data_saida = data_saida
        hospedagem.ativa = False
        hospedagem.save()

        quarto.status = 'LIMPEZA'
        quarto.save()

        # 5. Lançamento Financeiro Automático
        from financeiro.models import Conta, PlanoDeContas
        # Quem paga: Verifica se o hóspede tem empresa de convênio
        favorecido = hospedagem.hospede.empresa_convenio if hospedagem.hospede.empresa_convenio else hospedagem.hospede
        plano = PlanoDeContas.objects.filter(empresa=request.user.empresa, tipo='R').first()
        
        Conta.objects.create(
            empresa=request.user.empresa,
            descricao=f"Hospedagem Q-{quarto.numero} ({hospedagem.hospede.nome})",
            plano_de_contas=plano,
            cadastro=favorecido,
            valor=hospedagem.valor_total,
            data_vencimento=data_saida.date(),
            status='PENDENTE'
        )

        messages.success(request, f"Check-out realizado! Total: R$ {hospedagem.valor_total:.2f}")
        return redirect('hotel:mapa_quartos')

    return redirect('hotel:mapa_quartos')
