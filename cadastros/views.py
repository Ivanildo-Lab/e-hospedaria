# cadastros/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Cadastro
from .forms import CadastroForm

@login_required
def lista_hospedes(request):
    # Filtro base: mesma empresa do usuário
    queryset = Cadastro.objects.filter(empresa=request.user.empresa).order_by('nome')

    # Busca por texto (Nome ou CPF/CNPJ)
    q = request.GET.get('q')
    if q:
        queryset = queryset.filter(Q(nome__icontains=q) | Q(cpf_cnpj__icontains=q))

    # Filtro por Papel (Hóspede, Convênio, etc)
    papel = request.GET.get('papel')
    if papel:
        queryset = queryset.filter(papel=papel)

    return render(request, 'cadastros/lista_hospedes.html', {
        'cadastros': queryset,
        'filtro_q': q,
        'filtro_papel': papel
    })

@login_required
def novo_hospede(request):
    if request.method == 'POST':
        form = CadastroForm(request.POST, user=request.user)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.empresa = request.user.empresa
            obj.save()
            messages.success(request, f"{obj.nome} cadastrado com sucesso!")
            return redirect('lista_hospedes')
    else:
        form = CadastroForm(user=request.user)
    return render(request, 'cadastros/formulario.html', {'form': form, 'titulo': 'Novo Cadastro'})

@login_required
def editar_cadastro(request, pk):
    cadastro = get_object_or_404(Cadastro, pk=pk, empresa=request.user.empresa)
    if request.method == 'POST':
        form = CadastroForm(request.POST, instance=cadastro, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, f"Cadastro de {cadastro.nome} atualizado!")
            return redirect('lista_hospedes')
    else:
        form = CadastroForm(instance=cadastro, user=request.user)
    return render(request, 'cadastros/formulario.html', {'form': form, 'titulo': 'Editar Cadastro'})

@login_required
def excluir_cadastro(request, pk):
    cadastro = get_object_or_404(Cadastro, pk=pk, empresa=request.user.empresa)
    
    if request.method == 'POST':
        nome = cadastro.nome
        cadastro.delete()
        messages.success(request, f"O cadastro de '{nome}' foi removido com sucesso.")
        return redirect('lista_hospedes')
    
    # Se não for POST, volta para a lista (segurança)
    return redirect('lista_hospedes')