from django.db import models
from django.contrib.auth.models import User

class Alimento(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE) # Vincula o alimento ao usuário
    nome = models.CharField(max_length=100)
    calorias = models.FloatField()
    proteinas = models.FloatField(help_text="Gramas de proteína")
    carboidratos = models.FloatField(help_text="Gramas de carboidrato")
    gorduras = models.FloatField(help_text="Gramas de gordura")
    data_consumo = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.nome} - {self.usuario.username}"