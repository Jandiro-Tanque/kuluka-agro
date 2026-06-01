"""
Context processors para o app Pedidos
"""
from .models import Notificacao


def notificacoes_nao_lidas(request):
    """Adiciona contagem de notificações não lidas ao contexto global."""
    if request.user.is_authenticated:
        count = Notificacao.objects.filter(
            destinatario=request.user,
            lida=False
        ).count()
        return {'notificacoes_count': count}
    return {'notificacoes_count': 0}


def carrinho_quantidade(request):
    """Adiciona contagem de itens no carrinho ao contexto global."""
    carrinho = request.session.get('carrinho', {})
    count = sum(carrinho.values()) if carrinho else 0
    return {'carrinho_count': count}
