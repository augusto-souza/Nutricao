from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.db.models import Sum
from .forms import UsuarioRegistroForm, AlimentoForm
from .models import Alimento
from django.contrib import messages
from django.contrib.auth.models import User, Group # <--- Group é essencial aqui

# --- 1. REGISTRO DE USUÁRIO (COM ATRIBUIÇÃO DE GRUPO) ---
def registro(request):
    if request.method == 'POST':
        form = UsuarioRegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # --- NOVA LÓGICA: Atribuir Grupo ---
            # Pega o valor escolhido no select/radio ('Paciente' ou 'Nutricionista')
            tipo_usuario = form.cleaned_data.get('tipo_usuario')
            
            if tipo_usuario:
                try:
                    grupo = Group.objects.get(name=tipo_usuario)
                    user.groups.add(grupo)
                except Group.DoesNotExist:
                    # Fallback caso o grupo não exista no banco ainda
                    pass
            # -----------------------------------

            login(request, user)
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

# --- 4. DASHBOARD (LÓGICA DO PACIENTE) ---
@login_required
def dashboard(request):
    # LÓGICA DE REDIRECIONAMENTO:
    # Se for Nutricionista, ele vai para a lista de pacientes.
    if request.user.groups.filter(name='Nutricionista').exists():
        return redirect('lista_pacientes')

    # --- Visão do Paciente (Vê a própria dieta) ---
    alimentos = Alimento.objects.filter(usuario=request.user)
    
    # Cálculos
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
        'is_nutricionista': False # Paciente apenas visualiza
    }
    return render(request, 'dashboard.html', contexto)

# --- 4.1 LISTA DE PACIENTES (TELA INICIAL DO NUTRI) ---
@login_required
def lista_pacientes(request):
    # Apenas Nutricionistas acessam
    if not request.user.groups.filter(name='Nutricionista').exists():
        return redirect('dashboard')
    
    # Busca usuários comuns (exclui superusers e outros nutris)
    pacientes = User.objects.filter(is_superuser=False).exclude(groups__name='Nutricionista')
    
    return render(request, 'lista_pacientes.html', {'pacientes': pacientes})

# --- 4.2 DIETA DO PACIENTE (VISÃO DO NUTRI) ---
@login_required
def dieta_paciente(request, paciente_id):
    # Apenas Nutricionistas acessam
    if not request.user.groups.filter(name='Nutricionista').exists():
        return redirect('dashboard')

    paciente = get_object_or_404(User, id=paciente_id)
    alimentos = Alimento.objects.filter(usuario=paciente)

    # Cálculos
    calorias = alimentos.aggregate(Sum('calorias'))['calorias__sum'] or 0
    proteinas = alimentos.aggregate(Sum('proteinas'))['proteinas__sum'] or 0
    carboidratos = alimentos.aggregate(Sum('carboidratos'))['carboidratos__sum'] or 0
    gorduras = alimentos.aggregate(Sum('gorduras'))['gorduras__sum'] or 0

    contexto = {
        'paciente': paciente,
        'alimentos': alimentos,
        'total_calorias': int(round(calorias, 0)),
        'total_proteinas': round(proteinas, 1),
        'total_carboidratos': round(carboidratos, 1),
        'total_gorduras': round(gorduras, 1),
        'is_nutricionista': True # Habilita botões de edição/exclusão
    }
    return render(request, 'dieta_paciente.html', contexto)

# --- 5. ADICIONAR ALIMENTO (BLOQUEADO PARA PACIENTES) ---
@login_required
def adicionar_alimento(request):
    # Se o paciente tentar acessar /adicionar/, será bloqueado
    if not request.user.groups.filter(name='Nutricionista').exists():
        messages.error(request, "Ação não permitida: Apenas o nutricionista pode alterar a dieta.")
        return redirect('dashboard')

    # Nutricionista adicionando para si mesmo (uso pessoal, opcional)
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

# --- 5.1 ADICIONAR ALIMENTO PARA O PACIENTE (ESSENCIAL) ---
@login_required
def adicionar_alimento_paciente(request, paciente_id):
    if not request.user.groups.filter(name='Nutricionista').exists():
        return redirect('dashboard')

    paciente = get_object_or_404(User, id=paciente_id)

    if request.method == 'POST':
        form = AlimentoForm(request.POST)
        if form.is_valid():
            alimento = form.save(commit=False)
            alimento.usuario = paciente # O dono é o Paciente selecionado
            alimento.save()
            return redirect('dieta_paciente', paciente_id=paciente.id)
    else:
        form = AlimentoForm()
    
    return render(request, 'adicionar_alimento.html', {'form': form, 'paciente': paciente})

# --- 6. EDITAR ALIMENTO ---
@login_required
def editar_alimento(request, id):
    if not request.user.groups.filter(name='Nutricionista').exists():
        messages.error(request, "Permissão negada.")
        return redirect('dashboard')

    # Nutri pode editar qualquer alimento (não filtramos por usuario=request.user)
    alimento = get_object_or_404(Alimento, id=id)

    if request.method == 'POST':
        form = AlimentoForm(request.POST, instance=alimento)
        if form.is_valid():
            form.save()
            messages.success(request, "Alimento atualizado!")
            # Redireciona para a dieta do dono do alimento (Paciente)
            return redirect('dieta_paciente', paciente_id=alimento.usuario.id)
    else:
        form = AlimentoForm(instance=alimento)

    return render(request, 'editar_alimento.html', {'form': form, 'alimento': alimento})

# --- 7. DELETAR ALIMENTO ---
@login_required
def deletar_alimento(request, id):
    if not request.user.groups.filter(name='Nutricionista').exists():
        messages.error(request, "Permissão negada.")
        return redirect('dashboard')

    alimento = get_object_or_404(Alimento, id=id)
    paciente_id = alimento.usuario.id # Guarda o ID do dono antes de deletar

    if request.method == 'POST':
        alimento.delete()
        messages.success(request, "Alimento excluído!")
        # Redireciona para a dieta do Paciente
        return redirect('dieta_paciente', paciente_id=paciente_id)

    return render(request, 'deletar_alimento.html', {'alimento': alimento})