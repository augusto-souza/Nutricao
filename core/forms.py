from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Alimento
# Importa o módulo de tradução
from django.utils.translation import gettext_lazy as _

# Formulário de Cadastro de Usuário Personalizado
class UsuarioRegistroForm(UserCreationForm):
    # Adicionamos campos extras
    email = forms.EmailField(required=True, label="E-mail")
    first_name = forms.CharField(required=True, label="Nome")
    last_name = forms.CharField(required=True, label="Sobrenome")

    # CAMPO NOVO: Escolha de tipo
    TIPOS_USUARIO = (
        ('Paciente', 'Sou Paciente'),
        ('Nutricionista', 'Sou Nutricionista'),
    )
    tipo_usuario = forms.ChoiceField(
        choices=TIPOS_USUARIO,
        widget=forms.RadioSelect, # Cria bolinhas de seleção. Use forms.Select para lista suspensa.
        label="Tipo de Conta"
    )

    class Meta(UserCreationForm.Meta):
        model = User
        # Adicione os campos que você quer que apareçam no formulário
        fields = ('username', 'first_name', 'last_name', 'email')

class AlimentoForm(forms.ModelForm):
    class Meta:
        model = Alimento
        # Adicione 'proteinas', 'carboidratos', 'gorduras' na lista abaixo
        fields = ['nome', 'calorias', 'proteinas', 'carboidratos', 'gorduras']
        
        # Labels para ficarem bonitos na tela
        labels = {
            'nome': 'Nome do Alimento',
            'calorias': 'Calorias (kcal)',
            'proteinas': 'Proteínas (g)',
            'carboidratos': 'Carboidratos (g)',
            'gorduras': 'Gorduras (g)',
        }