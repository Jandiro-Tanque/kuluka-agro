"""
Admin customizado para o app Produtos
"""

from django.contrib import admin
from .models import Categoria, Produto


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    """
    Admin para categorias de produtos
    """
    list_display = ['nome', 'ativo']
    list_filter = ['ativo']
    search_fields = ['nome', 'descricao']
    ordering = ['nome']


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    """
    Admin para produtos
    """
    list_display = ['nome', 'fornecedor', 'categoria', 'preco', 'estoque', 'ativo', 'destaque', 'data_criacao']
    list_filter = ['ativo', 'destaque', 'categoria', 'unidade_medida', 'data_criacao']
    search_fields = ['nome', 'descricao', 'fornecedor__username', 'fornecedor__nome_empresa']
    ordering = ['-data_criacao']
    date_hierarchy = 'data_criacao'
    
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'categoria', 'descricao', 'imagem')
        }),
        ('Preço e Estoque', {
            'fields': ('preco', 'unidade_medida', 'estoque')
        }),
        ('Fornecedor', {
            'fields': ('fornecedor',)
        }),
        ('Status', {
            'fields': ('ativo', 'destaque')
        }),
    )
    
    raw_id_fields = ['fornecedor']
    list_editable = ['ativo', 'destaque']
