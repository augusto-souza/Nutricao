from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from .forms import UsuarioRegistroForm, AlimentoForm
from .models import Alimento

# 1. Cadastro de Usuário
def registro(request):
    if request.method == 'POST':
        form = UsuarioRegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user) # Faz login automático após cadastro
            return redirect('dashboard')
    else:
        form = UsuarioRegistroForm()
    return render(request, 'registro.html', {'form': form})

# 2. Dashboard (Lista alimentos do usuário logado)
@login_required
def dashboard(request):
    alimentos = Alimento.objects.filter(usuario=request.user) # Filtra apenas do usuário atual
    return render(request, 'dashboard.html', {'alimentos': alimentos})

# 3. Adicionar Alimento
@login_required
def adicionar_alimento(request):
    if request.method == 'POST':
        form = AlimentoForm(request.POST)
        if form.is_valid():
            alimento = form.save(commit=False)
            alimento.usuario = request.user # Define o dono do alimento
            alimento.save()
            return redirect('dashboard')
    else:
        form = AlimentoForm()
    return render(request, 'adicionar_alimento.html', {'form': form})