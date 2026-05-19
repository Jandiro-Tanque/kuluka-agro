"""
Views do app Contas - Autenticação e gerenciamento de perfil
"""

from django.views.generic import CreateView, UpdateView, TemplateView, DetailView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib import messages

from .models import Usuario
from .forms import RegistroUsuarioForm, PerfilUsuarioForm


class PaginaInicialView(TemplateView):
    """
    Página inicial do site
    """
    template_name = 'contas/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from produtos.models import Produto
        context['produtos_destaque'] = Produto.objects.filter(
            ativo=True, 
            destaque=True
        ).select_related('fornecedor', 'categoria')[:6]
        return context


class LoginUsuarioView(LoginView):
    """
    View de login customizada
    """
    template_name = 'contas/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return reverse_lazy('contas:perfil')
    
    def form_invalid(self, form):
        messages.error(self.request, 'Usuário ou senha inválidos.')
        return super().form_invalid(form)


class LogoutUsuarioView(LogoutView):
    """
    View de logout
    """
    next_page = reverse_lazy('contas:login')


class RegistroUsuarioView(CreateView):
    """
    View de registro de novos usuários
    """
    model = Usuario
    form_class = RegistroUsuarioForm
    template_name = 'contas/registro.html'
    success_url = reverse_lazy('contas:login')
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('contas:perfil')
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request, 
            'Conta criada com sucesso! Faça login para continuar.'
        )
        return response


class PerfilUsuarioView(LoginRequiredMixin, TemplateView):
    """
    View de perfil do usuário logado
    """
    template_name = 'contas/perfil.html'
    
    def get_template_names(self):
        if self.request.user.eh_fornecedor:
            return ['contas/perfil_fornecedor.html']
        return ['contas/perfil_produtor.html']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usuario = self.request.user
        
        if usuario.eh_fornecedor:
            from produtos.models import Produto
            context['meus_produtos'] = Produto.objects.filter(
                fornecedor=usuario
            ).order_by('-data_criacao')[:5]
            context['total_produtos'] = Produto.objects.filter(
                fornecedor=usuario
            ).count()
            from pedidos.models import Pedido, ItemPedido
            context['pedidos_recebidos'] = Pedido.objects.filter(
                itens__produto__fornecedor=usuario
            ).distinct().order_by('-data_criacao')[:5]
        else:
            from pedidos.models import Pedido
            context['meus_pedidos'] = Pedido.objects.filter(
                cliente=usuario
            ).order_by('-data_criacao')[:5]
        
        return context


class EditarPerfilView(LoginRequiredMixin, UpdateView):
    """
    View para editar perfil do usuário
    """
    model = Usuario
    form_class = PerfilUsuarioForm
    template_name = 'contas/editar_perfil.html'
    success_url = reverse_lazy('contas:perfil')
    
    def get_object(self, queryset=None):
        return self.request.user
    
    def form_valid(self, form):
        messages.success(self.request, 'Perfil atualizado com sucesso!')
        return super().form_valid(form)


class PerfilPublicoView(DetailView):
    """
    View para ver perfil público de outro usuário
    """
    model = Usuario
    template_name = 'contas/perfil_publico.html'
    context_object_name = 'perfil_usuario'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        usuario = self.get_object()
        
        if usuario.eh_fornecedor:
            from produtos.models import Produto
            context['produtos'] = Produto.objects.filter(
                fornecedor=usuario,
                ativo=True
            )
        
        return context
