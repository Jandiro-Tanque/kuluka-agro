"""
URLs do app Produtos
"""

from django.urls import path
from . import views

app_name = 'produtos'

urlpatterns = [
    path('', views.CatalogoProdutosView.as_view(), name='catalogo'),
    path('meus-produtos/', views.MeusProdutosView.as_view(), name='meus_produtos'),
    path('novo/', views.CriarProdutoView.as_view(), name='criar'),
    path('<int:pk>/', views.DetalheProdutoView.as_view(), name='detalhe'),
    path('<int:pk>/editar/', views.EditarProdutoView.as_view(), name='editar'),
    path('<int:pk>/excluir/', views.ExcluirProdutoView.as_view(), name='excluir'),
]
