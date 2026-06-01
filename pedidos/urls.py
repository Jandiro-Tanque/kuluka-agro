"""
URLs do app Pedidos
"""

from django.urls import path
from . import views

app_name = 'pedidos'

urlpatterns = [
    path('carrinho/', views.CarrinhoView.as_view(), name='carrinho'),
    path('carrinho/adicionar/<int:pk>/', views.AdicionarCarrinhoView.as_view(), name='adicionar'),
    path('carrinho/remover/<int:pk>/', views.RemoverCarrinhoView.as_view(), name='remover'),
    path('carrinho/atualizar/<int:pk>/', views.AtualizarCarrinhoView.as_view(), name='atualizar'),
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('meus-pedidos/', views.MeusPedidosView.as_view(), name='meus_pedidos'),
    path('pedido/<int:pk>/', views.DetalhePedidoView.as_view(), name='detalhe_pedido'),
    path('recebidos/', views.PedidosRecebidosView.as_view(), name='pedidos_recebidos'),
    path('pedido/<int:pk>/status/', views.AtualizarStatusPedidoView.as_view(), name='atualizar_status'),
    # Novas URLs
    path('pedido/<int:pk>/confirmar-entrega/', views.ConfirmarEntregaView.as_view(), name='confirmar_entrega'),
    path('pedido/<int:pk>/avaliar/', views.AvaliarProdutoView.as_view(), name='avaliar_produto'),
    path('notificacoes/', views.NotificacoesView.as_view(), name='notificacoes'),
    path('notificacoes/<int:pk>/lida/', views.MarcarNotifLidaView.as_view(), name='marcar_lida'),
]
