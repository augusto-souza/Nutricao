from django.contrib import admin
from .models import Alimento

# Opção 1: Simples (Apenas registra)
# admin.site.register(Alimento)

# Opção 2: Avançada (Melhora a visualização das colunas)
@admin.register(Alimento)
class AlimentoAdmin(admin.ModelAdmin):
    # Campos que aparecem na lista (tabela)
    list_display = ('nome', 'calorias', 'proteinas', 'carboidratos', 'gorduras', 'usuario', 'data_consumo')
    
    # Filtros laterais para facilitar a busca
    list_filter = ('usuario', 'data_consumo')
    
    # Campo de busca (pelo nome do alimento ou nome do usuário)
    search_fields = ('nome', 'usuario__username')