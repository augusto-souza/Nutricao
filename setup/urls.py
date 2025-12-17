from django.contrib import admin
from django.urls import path
from core import views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Autenticação
    path('registro/', views.registro, name='registro'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Sistema Principal
    path('', views.dashboard, name='dashboard'),
    path('adicionar/', views.adicionar_alimento, name='adicionar_alimento'),
    
    # --- NOVAS ROTAS (CRUD) ---
    path('editar/<int:id>/', views.editar_alimento, name='editar_alimento'),
    path('deletar/<int:id>/', views.deletar_alimento, name='deletar_alimento'),
]