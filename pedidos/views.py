"""
Views do app Pedidos - Carrinho, checkout, notificações, avaliações
"""

from django.views.generic import ListView, DetailView, TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse

from produtos.models import Produto
from .models import Pedido, ItemPedido, Notificacao, AvaliacaoProduto


def criar_notificacao(pedido, tipo, mensagem):
    """Helper para criar notificação para o produtor."""
    Notificacao.objects.create(
        destinatario=pedido.cliente,
        pedido=pedido,
        tipo=tipo,
        mensagem=mensagem,
    )


class CarrinhoView(TemplateView):
    """
    Visualiza o carrinho de compras
    """
    template_name = 'pedidos/carrinho.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        carrinho = self.request.session.get('carrinho', {})
        
        itens = []
        total = 0
        
        for produto_id, quantidade in carrinho.items():
            try:
                produto = Produto.objects.get(pk=produto_id, ativo=True)
                subtotal = produto.preco * quantidade
                total += subtotal
                itens.append({
                    'produto': produto,
                    'quantidade': quantidade,
                    'subtotal': subtotal,
                })
            except Produto.DoesNotExist:
                pass
        
        context['itens'] = itens
        context['total'] = total
        context['total_formatado'] = f"Kz {total:,.2f}"
        return context


class AdicionarCarrinhoView(View):
    def post(self, request, pk):
        produto = get_object_or_404(Produto, pk=pk, ativo=True)
        quantidade = int(request.POST.get('quantidade', 1))
        
        carrinho = request.session.get('carrinho', {})
        produto_id = str(pk)
        
        if produto_id in carrinho:
            carrinho[produto_id] += quantidade
        else:
            carrinho[produto_id] = quantidade
        
        if carrinho[produto_id] > produto.estoque:
            carrinho[produto_id] = produto.estoque
            messages.warning(request, f'Quantidade ajustada para o estoque disponível: {produto.estoque}')
        
        request.session['carrinho'] = carrinho
        messages.success(request, f'{produto.nome} adicionado ao carrinho!')
        
        next_url = request.POST.get('next', request.META.get('HTTP_REFERER', '/'))
        return redirect(next_url)


class RemoverCarrinhoView(View):
    def post(self, request, pk):
        carrinho = request.session.get('carrinho', {})
        produto_id = str(pk)
        
        if produto_id in carrinho:
            del carrinho[produto_id]
            request.session['carrinho'] = carrinho
            messages.success(request, 'Produto removido do carrinho.')
        
        return redirect('pedidos:carrinho')


class AtualizarCarrinhoView(View):
    def post(self, request, pk):
        quantidade = int(request.POST.get('quantidade', 1))
        produto = get_object_or_404(Produto, pk=pk, ativo=True)
        
        carrinho = request.session.get('carrinho', {})
        produto_id = str(pk)
        
        if quantidade > 0:
            if quantidade > produto.estoque:
                quantidade = produto.estoque
                messages.warning(request, f'Quantidade ajustada para o estoque disponível: {produto.estoque}')
            carrinho[produto_id] = quantidade
        else:
            if produto_id in carrinho:
                del carrinho[produto_id]
        
        request.session['carrinho'] = carrinho
        return redirect('pedidos:carrinho')


class CheckoutView(LoginRequiredMixin, TemplateView):
    template_name = 'pedidos/checkout.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        carrinho = self.request.session.get('carrinho', {})
        
        itens = []
        total = 0
        
        for produto_id, quantidade in carrinho.items():
            try:
                produto = Produto.objects.get(pk=produto_id, ativo=True)
                subtotal = produto.preco * quantidade
                total += subtotal
                itens.append({
                    'produto': produto,
                    'quantidade': quantidade,
                    'subtotal': subtotal,
                })
            except Produto.DoesNotExist:
                pass
        
        context['itens'] = itens
        context['total'] = total
        context['total_formatado'] = f"Kz {total:,.2f}"
        return context
    
    def post(self, request):
        carrinho = request.session.get('carrinho', {})
        
        if not carrinho:
            messages.error(request, 'Seu carrinho está vazio.')
            return redirect('pedidos:carrinho')
        
        endereco = request.POST.get('endereco', request.user.endereco)
        observacoes = request.POST.get('observacoes', '')
        
        if not endereco:
            messages.error(request, 'Por favor, informe o endereço de entrega.')
            return redirect('pedidos:checkout')
        
        pedido = Pedido.objects.create(
            cliente=request.user,
            endereco_entrega=endereco,
            observacoes=observacoes,
        )
        
        for produto_id, quantidade in carrinho.items():
            try:
                produto = Produto.objects.get(pk=produto_id, ativo=True)
                ItemPedido.objects.create(
                    pedido=pedido,
                    produto=produto,
                    quantidade=quantidade,
                    preco_unitario=produto.preco,
                )
                produto.estoque -= quantidade
                produto.save()
            except Produto.DoesNotExist:
                pass
        
        pedido.calcular_total()
        request.session['carrinho'] = {}
        
        # Notificar o produtor que o pedido foi criado
        criar_notificacao(
            pedido,
            Notificacao.TipoNotificacao.STATUS_ATUALIZADO,
            f'O teu pedido #{pedido.pk} foi realizado com sucesso e está a aguardar confirmação do fornecedor.'
        )
        
        messages.success(request, f'Pedido #{pedido.pk} realizado com sucesso!')
        return redirect('pedidos:detalhe_pedido', pk=pedido.pk)


class MeusPedidosView(LoginRequiredMixin, ListView):
    model = Pedido
    template_name = 'pedidos/meus_pedidos.html'
    context_object_name = 'pedidos'
    paginate_by = 10
    
    def get_queryset(self):
        return Pedido.objects.filter(
            cliente=self.request.user
        ).prefetch_related('itens__produto').order_by('-data_criacao')


class DetalhePedidoView(LoginRequiredMixin, DetailView):
    model = Pedido
    template_name = 'pedidos/detalhe_pedido.html'
    context_object_name = 'pedido'
    
    def get_queryset(self):
        return Pedido.objects.filter(
            cliente=self.request.user
        ).prefetch_related('itens__produto')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        pedido = self.object
        # Verificar quais itens já foram avaliados
        avaliacoes_feitas = AvaliacaoProduto.objects.filter(
            pedido=pedido,
            avaliador=self.request.user
        ).values_list('produto_id', flat=True)
        context['avaliacoes_feitas'] = list(avaliacoes_feitas)
        return context


class PedidosRecebidosView(LoginRequiredMixin, ListView):
    model = Pedido
    template_name = 'pedidos/pedidos_recebidos.html'
    context_object_name = 'pedidos'
    paginate_by = 10
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.eh_fornecedor:
            messages.error(request, 'Apenas fornecedores podem acessar esta página.')
            return redirect('contas:perfil')
        return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        return Pedido.objects.filter(
            itens__produto__fornecedor=self.request.user
        ).distinct().prefetch_related('itens__produto').order_by('-data_criacao')


class AtualizarStatusPedidoView(LoginRequiredMixin, View):
    """
    Atualiza status de um pedido (para fornecedores)
    Quando status = ENTREGUE, notifica produtor para confirmar.
    """
    def post(self, request, pk):
        if not request.user.eh_fornecedor:
            messages.error(request, 'Apenas fornecedores podem atualizar pedidos.')
            return redirect('contas:perfil')
        
        pedido = get_object_or_404(Pedido, pk=pk)
        
        tem_produtos = pedido.itens.filter(produto__fornecedor=request.user).exists()
        if not tem_produtos:
            messages.error(request, 'Você não tem permissão para atualizar este pedido.')
            return redirect('pedidos:pedidos_recebidos')
        
        novo_status = request.POST.get('status')
        if novo_status in dict(Pedido.StatusPedido.choices):
            status_anterior = pedido.status
            pedido.status = novo_status
            # Se marcar como ENTREGUE, resetar confirmação do produtor
            if novo_status == Pedido.StatusPedido.ENTREGUE:
                pedido.entrega_confirmada = False
            pedido.save()
            
            # Criar notificação para o produtor
            labels = dict(Pedido.StatusPedido.choices)
            if novo_status == Pedido.StatusPedido.ENTREGUE:
                tipo = Notificacao.TipoNotificacao.ENTREGUE
                mensagem = (
                    f'🚚 O teu pedido #{pedido.pk} foi marcado como Entregue pelo fornecedor. '
                    f'Por favor confirma se o pedido foi realmente recebido.'
                )
            else:
                tipo = Notificacao.TipoNotificacao.STATUS_ATUALIZADO
                mensagem = (
                    f'📦 O estado do teu pedido #{pedido.pk} foi actualizado: '
                    f'{labels.get(status_anterior, status_anterior)} → {labels.get(novo_status, novo_status)}.'
                )
            
            criar_notificacao(pedido, tipo, mensagem)
            messages.success(request, f'Status do pedido #{pedido.pk} atualizado!')
        
        return redirect('pedidos:pedidos_recebidos')


class ConfirmarEntregaView(LoginRequiredMixin, View):
    """
    Produtor confirma que o pedido foi realmente entregue.
    Após confirmar, pode avaliar os produtos.
    """
    def post(self, request, pk):
        pedido = get_object_or_404(Pedido, pk=pk, cliente=request.user)
        
        if pedido.status != Pedido.StatusPedido.ENTREGUE:
            messages.error(request, 'Este pedido ainda não foi marcado como entregue.')
            return redirect('pedidos:detalhe_pedido', pk=pk)
        
        pedido.entrega_confirmada = True
        pedido.save()
        
        messages.success(request, f'Entrega do pedido #{pedido.pk} confirmada! Agora podes avaliar os produtos.')
        return redirect('pedidos:detalhe_pedido', pk=pk)


class AvaliarProdutoView(LoginRequiredMixin, View):
    """
    Produtor avalia um produto após confirmar entrega.
    """
    def post(self, request, pk):
        pedido = get_object_or_404(Pedido, pk=pk, cliente=request.user)
        
        if not pedido.entrega_confirmada:
            messages.error(request, 'Confirma primeiro a entrega para poderes avaliar.')
            return redirect('pedidos:detalhe_pedido', pk=pk)
        
        produto_id = request.POST.get('produto_id')
        nota = request.POST.get('nota')
        comentario = request.POST.get('comentario', '')
        
        if not produto_id or not nota:
            messages.error(request, 'Nota e produto são obrigatórios.')
            return redirect('pedidos:detalhe_pedido', pk=pk)
        
        produto = get_object_or_404(Produto, pk=produto_id)
        
        # Verificar se o produto faz parte deste pedido
        if not pedido.itens.filter(produto=produto).exists():
            messages.error(request, 'Este produto não faz parte do teu pedido.')
            return redirect('pedidos:detalhe_pedido', pk=pk)
        
        avaliacao, created = AvaliacaoProduto.objects.update_or_create(
            pedido=pedido,
            produto=produto,
            avaliador=request.user,
            defaults={
                'nota': int(nota),
                'comentario': comentario,
            }
        )
        
        if created:
            messages.success(request, f'Avaliação enviada para "{produto.nome}"!')
        else:
            messages.success(request, f'Avaliação de "{produto.nome}" actualizada!')
        
        return redirect('pedidos:detalhe_pedido', pk=pk)


class NotificacoesView(LoginRequiredMixin, ListView):
    """
    Lista todas as notificações do utilizador
    """
    model = Notificacao
    template_name = 'pedidos/notificacoes.html'
    context_object_name = 'notificacoes'
    
    def get_queryset(self):
        qs = Notificacao.objects.filter(destinatario=self.request.user).order_by('-data_criacao')
        # Marcar todas como lidas ao visualizar
        qs.update(lida=True)
        return qs


class MarcarNotifLidaView(LoginRequiredMixin, View):
    def post(self, request, pk):
        notif = get_object_or_404(Notificacao, pk=pk, destinatario=request.user)
        notif.lida = True
        notif.save()
        return JsonResponse({'ok': True})
