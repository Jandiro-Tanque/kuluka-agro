"""
URLs do app Contas
"""

from django.urls import path
from . import views

app_name = 'contas'

urlpatterns = [
    path('', views.PaginaInicialView.as_view(), name='home'),
    path('login/', views.LoginUsuarioView.as_view(), name='login'),
    path('logout/', views.LogoutUsuarioView.as_view(), name='logout'),
    path('registro/', views.RegistroUsuarioView.as_view(), name='registro'),
    path('perfil/', views.PerfilUsuarioView.as_view(), name='perfil'),
    path('perfil/editar/', views.EditarPerfilView.as_view(), name='editar_perfil'),
    path('usuario/<int:pk>/', views.PerfilPublicoView.as_view(), name='perfil_publico'),
]
