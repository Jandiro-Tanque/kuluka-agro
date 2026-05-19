"""
Views do app Pedidos - Carrinho e checkout
"""

from django.views.generic import ListView, DetailView, TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse

from produtos.models import Produto
from .models import Pedido, ItemPedido


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
    """
    Adiciona produto ao carrinho
    """
    def post(self, request, pk):
        produto = get_object_or_404(Produto, pk=pk, ativo=True)
        quantidade = int(request.POST.get('quantidade', 1))
        
        carrinho = request.session.get('carrinho', {})
        produto_id = str(pk)
        
        if produto_id in carrinho:
            carrinho[produto_id] += quantidade
        else:
            carrinho[produto_id] = quantidade
        
        # Limitar ao estoque disponível
        if carrinho[produto_id] > produto.estoque:
            carrinho[produto_id] = produto.estoque
            messages.warning(request, f'Quantidade ajustada para o estoque disponível: {produto.estoque}')
        
        request.session['carrinho'] = carrinho
        messages.success(request, f'{produto.nome} adicionado ao carrinho!')
        
        # Retorna para a página anterior ou para o catálogo
        next_url = request.POST.get('next', request.META.get('HTTP_REFERER', '/'))
        return redirect(next_url)


class RemoverCarrinhoView(View):
    """
    Remove produto do carrinho
    """
    def post(self, request, pk):
        carrinho = request.session.get('carrinho', {})
        produto_id = str(pk)
        
        if produto_id in carrinho:
            del carrinho[produto_id]
            request.session['carrinho'] = carrinho
            messages.success(request, 'Produto removido do carrinho.')
        
        return redirect('pedidos:carrinho')


class AtualizarCarrinhoView(View):
    """
    Atualiza quantidade de um item no carrinho
    """
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
    """
    Página de checkout
    """
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
        
        # Criar pedido
        pedido = Pedido.objects.create(
            cliente=request.user,
            endereco_entrega=endereco,
            observacoes=observacoes,
        )
        
        # Adicionar itens
        for produto_id, quantidade in carrinho.items():
            try:
                produto = Produto.objects.get(pk=produto_id, ativo=True)
                ItemPedido.objects.create(
                    pedido=pedido,
                    produto=produto,
                    quantidade=quantidade,
                    preco_unitario=produto.preco,
                )
                # Atualizar estoque
                produto.estoque -= quantidade
                produto.save()
            except Produto.DoesNotExist:
                pass
        
        # Calcular total
        pedido.calcular_total()
        
        # Limpar carrinho
        request.session['carrinho'] = {}
        
        messages.success(request, f'Pedido #{pedido.pk} realizado com sucesso!')
        return redirect('pedidos:detalhe_pedido', pk=pedido.pk)


class MeusPedidosView(LoginRequiredMixin, ListView):
    """
    Lista pedidos do usuário
    """
    model = Pedido
    template_name = 'pedidos/meus_pedidos.html'
    context_object_name = 'pedidos'
    paginate_by = 10
    
    def get_queryset(self):
        return Pedido.objects.filter(
            cliente=self.request.user
        ).prefetch_related('itens__produto').order_by('-data_criacao')


class DetalhePedidoView(LoginRequiredMixin, DetailView):
    """
    Detalhes de um pedido
    """
    model = Pedido
    template_name = 'pedidos/detalhe_pedido.html'
    context_object_name = 'pedido'
    
    def get_queryset(self):
        return Pedido.objects.filter(
            cliente=self.request.user
        ).prefetch_related('itens__produto')


class PedidosRecebidosView(LoginRequiredMixin, ListView):
    """
    Lista pedidos recebidos pelo fornecedor
    """
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
    """
    def post(self, request, pk):
        if not request.user.eh_fornecedor:
            messages.error(request, 'Apenas fornecedores podem atualizar pedidos.')
            return redirect('contas:perfil')
        
        pedido = get_object_or_404(Pedido, pk=pk)
        
        # Verificar se o fornecedor tem produtos neste pedido
        tem_produtos = pedido.itens.filter(produto__fornecedor=request.user).exists()
        if not tem_produtos:
            messages.error(request, 'Você não tem permissão para atualizar este pedido.')
            return redirect('pedidos:pedidos_recebidos')
        
        novo_status = request.POST.get('status')
        if novo_status in dict(Pedido.StatusPedido.choices):
            pedido.status = novo_status
            pedido.save()
            messages.success(request, f'Status do pedido #{pedido.pk} atualizado!')
        
        return redirect('pedidos:pedidos_recebidos')
