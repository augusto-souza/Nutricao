from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Alimento

# Formulário de Cadastro de Usuário Personalizado
class UsuarioRegistroForm(UserCreationForm):
    email = forms.EmailField(required=True) # Força o email a ser obrigatório

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name']

# Formulário de Alimento
class AlimentoForm(forms.ModelForm):
    class Meta:
        model = Alimento
        fields = ['nome', 'calorias', 'proteinas', 'carboidratos', 'gorduras']