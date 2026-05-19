"""
Admin customizado para o app Contas
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    """
    Admin customizado para usuários KULUKA AGRO
    """
    list_display = ['username', 'email', 'first_name', 'last_name', 'tipo', 'is_active', 'data_criacao']
    list_filter = ['tipo', 'is_active', 'is_staff', 'data_criacao']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'nome_empresa']
    ordering = ['-data_criacao']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Informações KULUKA AGRO', {
            'fields': (
                'tipo',
                'telefone',
                'endereco',
                'cidade',
                'provincia',
                'foto_perfil',
                'descricao',
            )
        }),
        ('Dados do Fornecedor', {
            'fields': (
                'nome_empresa',
                'nif',
            ),
            'classes': ('collapse',)
        }),
        ('Dados do Produtor', {
            'fields': (
                'area_cultivo',
                'tipos_cultivo',
            ),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Tipo de Usuário', {
            'fields': ('tipo',)
        }),
    )


# Customização do Admin Site
admin.site.site_header = 'KULUKA AGRO - Administração'
admin.site.site_title = 'KULUKA AGRO Admin'
admin.site.index_title = 'Painel de Controle'
