"""
Views do app Produtos - Catálogo e gerenciamento de produtos
"""

from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib import messages
from django.db.models import Q

from .models import Produto, Categoria
from .forms import ProdutoForm


class FornecedorRequiredMixin(UserPassesTestMixin):
    """
    Mixin que verifica se o usuário é fornecedor
    """
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.eh_fornecedor
    
    def handle_no_permission(self):
        messages.error(self.request, 'Apenas fornecedores podem acessar esta página.')
        return redirect('contas:perfil')


class CatalogoProdutosView(ListView):
    """
    Lista todos os produtos disponíveis
    """
    model = Produto
    template_name = 'produtos/catalogo.html'
    context_object_name = 'produtos'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Produto.objects.filter(ativo=True).select_related(
            'fornecedor', 'categoria'
        )
        
        # Filtro por busca
        busca = self.request.GET.get('busca')
        if busca:
            queryset = queryset.filter(
                Q(nome__icontains=busca) |
                Q(descricao__icontains=busca) |
                Q(fornecedor__username__icontains=busca)
            )
        
        # Filtro por categoria
        categoria_id = self.request.GET.get('categoria')
        if categoria_id:
            queryset = queryset.filter(categoria_id=categoria_id)
        
        # Ordenação
        ordenar = self.request.GET.get('ordenar', '-data_criacao')
        if ordenar in ['preco', '-preco', 'nome', '-nome', '-data_criacao']:
            queryset = queryset.order_by(ordenar)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categorias'] = Categoria.objects.filter(ativo=True)
        context['busca'] = self.request.GET.get('busca', '')
        context['categoria_selecionada'] = self.request.GET.get('categoria', '')
        context['ordenar'] = self.request.GET.get('ordenar', '-data_criacao')
        return context


class DetalheProdutoView(DetailView):
    """
    Detalhes de um produto específico
    """
    model = Produto
    template_name = 'produtos/detalhe.html'
    context_object_name = 'produto'
    
    def get_queryset(self):
        return Produto.objects.filter(ativo=True).select_related(
            'fornecedor', 'categoria'
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Produtos relacionados da mesma categoria
        produto = self.get_object()
        if produto.categoria:
            context['produtos_relacionados'] = Produto.objects.filter(
                categoria=produto.categoria,
                ativo=True
            ).exclude(pk=produto.pk)[:4]
        return context


class MeusProdutosView(LoginRequiredMixin, FornecedorRequiredMixin, ListView):
    """
    Lista produtos do fornecedor logado
    """
    model = Produto
    template_name = 'produtos/meus_produtos.html'
    context_object_name = 'produtos'
    paginate_by = 10
    
    def get_queryset(self):
        return Produto.objects.filter(
            fornecedor=self.request.user
        ).select_related('categoria').order_by('-data_criacao')


class CriarProdutoView(LoginRequiredMixin, FornecedorRequiredMixin, CreateView):
    """
    Criar novo produto
    """
    model = Produto
    form_class = ProdutoForm
    template_name = 'produtos/form_produto.html'
    success_url = reverse_lazy('produtos:meus_produtos')
    
    def form_valid(self, form):
        form.instance.fornecedor = self.request.user
        messages.success(self.request, 'Produto criado com sucesso!')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Adicionar Novo Produto'
        context['botao'] = 'Criar Produto'
        return context


class EditarProdutoView(LoginRequiredMixin, FornecedorRequiredMixin, UpdateView):
    """
    Editar produto existente
    """
    model = Produto
    form_class = ProdutoForm
    template_name = 'produtos/form_produto.html'
    success_url = reverse_lazy('produtos:meus_produtos')
    
    def get_queryset(self):
        return Produto.objects.filter(fornecedor=self.request.user)
    
    def form_valid(self, form):
        messages.success(self.request, 'Produto atualizado com sucesso!')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titulo'] = 'Editar Produto'
        context['botao'] = 'Salvar Alterações'
        return context


class ExcluirProdutoView(LoginRequiredMixin, FornecedorRequiredMixin, DeleteView):
    """
    Excluir produto
    """
    model = Produto
    template_name = 'produtos/confirmar_exclusao.html'
    success_url = reverse_lazy('produtos:meus_produtos')
    
    def get_queryset(self):
        return Produto.objects.filter(fornecedor=self.request.user)
    
    def form_valid(self, form):
        messages.success(self.request, 'Produto excluído com sucesso!')
        return super().form_valid(form)
