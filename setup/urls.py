from django.contrib import admin
from django.urls import path
from core import views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Rotas de Autenticação
    path('registro/', views.registro, name='registro'),
    path('login/', views.login_view, name='login'),      # <-- Atenção aqui: login_view
    path('logout/', views.logout_view, name='logout'),   # <-- Atenção aqui: logout_view

    # Rotas do Sistema
    path('', views.dashboard, name='dashboard'),
    path('adicionar/', views.adicionar_alimento, name='adicionar_alimento'),
]