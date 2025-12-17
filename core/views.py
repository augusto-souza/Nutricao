from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Sum
from .forms import UsuarioRegistroForm, AlimentoForm
from .models import Alimento
from django.contrib import messages

# --- 1. REGISTRO DE USUÁRIO ---
def registro(request):
    if request.method == 'POST':
        form = UsuarioRegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # Loga o usuário automaticamente
            return redirect('dashboard')
    else:
        form = UsuarioRegistroForm()
    return render(request, 'registro.html', {'form': form})

# --- 2. LOGIN ---
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

# --- 4. DASHBOARD (COM CONTROLE DE PERMISSÃO) ---
@login_required
def dashboard(request):
    # Filtra apenas os alimentos do usuário logado
    alimentos = Alimento.objects.filter(usuario=request.user)

    # Verifica se o usuário pertence ao grupo 'Nutricionista'
    # Retorna True ou False
    is_nutricionista = request.user.groups.filter(name='Nutricionista').exists()

    # Cálculos de agregação
    calorias = alimentos.aggregate(Sum('calorias'))['calorias__sum'] or 0
    proteinas = alimentos.aggregate(Sum('proteinas'))['proteinas__sum'] or 0
    carboidratos = alimentos.aggregate(Sum('carboidratos'))['carboidratos__sum'] or 0
    gorduras = alimentos.aggregate(Sum('gorduras'))['gorduras__sum'] or 0

    contexto = {
        'alimentos': alimentos,
        'total_calorias': int(round(calorias, 0)),
        'total_proteinas': round(proteinas, 1),
        'total_carboidratos': round(carboidratos, 1),
        'total_gorduras': round(gorduras, 1),
        'is_nutricionista': is_nutricionista, # <-- Enviando a permissão para o HTML
    }

    return render(request, 'dashboard.html', contexto)

# --- 5. ADICIONAR ALIMENTO ---
@login_required
def adicionar_alimento(request):
    # Opcional: Se quiser que APENAS nutri adicione, coloque a trava aqui também.
    # Por enquanto, deixei liberado para todos registrarem o que comeram.
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

# --- 6. EDITAR ALIMENTO (PROTEGIDO) ---
@login_required
def editar_alimento(request, id):
    # TRAVA DE SEGURANÇA: Verifica se é Nutricionista
    if not request.user.groups.filter(name='Nutricionista').exists():
        messages.error(request, "Permissão negada: Apenas nutricionistas podem editar.")
        return redirect('dashboard')

    # Busca o alimento (mantendo a segurança de ser do próprio usuário)
    alimento = get_object_or_404(Alimento, id=id, usuario=request.user)

    if request.method == 'POST':
        form = AlimentoForm(request.POST, instance=alimento)
        if form.is_valid():
            form.save()
            messages.success(request, "Alimento atualizado com sucesso!")
            return redirect('dashboard')
    else:
        form = AlimentoForm(instance=alimento)

    return render(request, 'editar_alimento.html', {'form': form, 'alimento': alimento})

# --- 7. DELETAR ALIMENTO (PROTEGIDO) ---
@login_required
def deletar_alimento(request, id):
    # TRAVA DE SEGURANÇA: Verifica se é Nutricionista
    if not request.user.groups.filter(name='Nutricionista').exists():
        messages.error(request, "Permissão negada: Apenas nutricionistas podem excluir.")
        return redirect('dashboard')

    alimento = get_object_or_404(Alimento, id=id, usuario=request.user)

    if request.method == 'POST':
        alimento.delete()
        messages.success(request, "Alimento excluído com sucesso!")
        return redirect('dashboard')

    return render(request, 'deletar_alimento.html', {'alimento': alimento})