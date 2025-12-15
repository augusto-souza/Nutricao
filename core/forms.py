from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Alimento
# Importa o módulo de tradução
from django.utils.translation import gettext_lazy as _

# Formulário de Cadastro de Usuário Personalizado
class UsuarioRegistroForm(UserCreationForm):
    # Traduzindo o campo email e first_name
    email = forms.EmailField(required=True, label=_('E-mail'))
    first_name = forms.CharField(max_length=30, required=True, label=_('Nome'))

    class Meta:
        model = User
        # Os campos 'username' e 'password' são traduzidos pelo próprio Django
        fields = ['username', 'email', 'first_name']
        
        # Traduzindo o help text do username
        help_texts = {
            'username': _('Obrigatório. 150 caracteres ou menos. Apenas letras, dígitos e @/./+/-/_.'),
        }
        # Traduzindo a label do username
        labels = {
            'username': _('Nome de Usuário'),
        }

class AlimentoForm(forms.ModelForm):
    class Meta:
        model = Alimento
        fields = ['nome', 'calorias'] # <--- Deixamos apenas o que você quer
        
        labels = {
            'nome': 'Nome do Alimento',
            'calorias': 'Calorias (kcal)',
        }