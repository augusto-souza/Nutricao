from django.db import models  # <--- Essa linha é OBRIGATÓRIA
from django.contrib.auth.models import User # <--- Essa linha é necessária para o usuario

class Alimento(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    nome = models.CharField(max_length=100)
    calorias = models.FloatField()
    
    # Macros com valor padrão 0, já que não vamos pedir no formulário agora
    proteinas = models.FloatField(default=0)
    carboidratos = models.FloatField(default=0)
    gorduras = models.FloatField(default=0)
    
    data_consumo = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.nome} - {self.usuario.username}"