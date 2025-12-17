from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Sum
from .forms import UsuarioRegistroForm, AlimentoForm
from .models import Alimento

# --- 1. REGISTRO DE USUÁRIO ---
def registro(request):
    if request.method == 'POST':
        form = UsuarioRegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Loga o usuário automaticamente após cadastro
            return redirect('dashboard')
    else:
        form = UsuarioRegistroForm()
    return render(request, 'registro.html', {'form': form})

# --- 2. LOGIN (OTIMIZADO) ---
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

# --- 3. LOGOUT ---
def logout_view(request):
    logout(request)
    return redirect('login')

# --- 4. DASHBOARD (COM SOMA E ARREDONDAMENTO) ---
@login_required
def dashboard(request):
    alimentos = Alimento.objects.filter(usuario=request.user)

    # Soma os valores (se for None, vira 0)
    calorias = alimentos.aggregate(Sum('calorias'))['calorias__sum'] or 0
    proteinas = alimentos.aggregate(Sum('proteinas'))['proteinas__sum'] or 0
    carboidratos = alimentos.aggregate(Sum('carboidratos'))['carboidratos__sum'] or 0
    gorduras = alimentos.aggregate(Sum('gorduras'))['gorduras__sum'] or 0

    # Arredondamento no Python para evitar erros no Template
    contexto = {
        'alimentos': alimentos,
        'total_calorias': int(round(calorias, 0)),
        'total_proteinas': round(proteinas, 1),
        'total_carboidratos': round(carboidratos, 1),
        'total_gorduras': round(gorduras, 1),
    }

    return render(request, 'dashboard.html', contexto)

# --- 5. ADICIONAR ALIMENTO ---
@login_required
def adicionar_alimento(request):
    if request.method == 'POST':
        form = AlimentoForm(request.POST)
        if form.is_valid():
            alimento = form.save(commit=False)
            alimento.usuario = request.user
            alimento.save()
            return redirect('dashboard')
    else:
        form = AlimentoForm()
    return render(request, 'adicionar_alimento.html', {'form': form})

@login_required
def editar_alimento(request, id):
    # Busca o alimento pelo ID, mas SÓ se pertencer ao usuário logado (Segurança!)
    alimento = get_object_or_404(Alimento, id=id, usuario=request.user)

    if request.method == 'POST':
        # Carrega o formulário com os dados do banco (instance=alimento)
        form = AlimentoForm(request.POST, instance=alimento)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        # Se for GET, mostra o formulário preenchido
        form = AlimentoForm(instance=alimento)

    return render(request, 'editar_alimento.html', {'form': form, 'alimento': alimento})

# --- DELETAR ALIMENTO (DELETE) ---
@login_required
def deletar_alimento(request, id):
    # Busca o alimento com segurança
    alimento = get_object_or_404(Alimento, id=id, usuario=request.user)

    if request.method == 'POST':
        # Se confirmou a exclusão
        alimento.delete()
        return redirect('dashboard')

    # Se for GET, mostra a página de confirmação ("Tem certeza?")
    return render(request, 'deletar_alimento.html', {'alimento': alimento})