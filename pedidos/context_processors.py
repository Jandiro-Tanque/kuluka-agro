"""
Context processors do app Pedidos
"""


def carrinho_quantidade(request):
    """
    Adiciona a quantidade de itens no carrinho ao contexto global
    """
    carrinho = request.session.get('carrinho', {})
    quantidade_total = sum(carrinho.values())
    return {
        'carrinho_quantidade': quantidade_total
    }
