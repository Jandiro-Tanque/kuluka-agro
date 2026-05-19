"""
Admin customizado para o app Pedidos
"""

from django.contrib import admin
from .models import Pedido, ItemPedido


class ItemPedidoInline(admin.TabularInline):
    """
    Inline para itens do pedido
    """
    model = ItemPedido
    extra = 0
    readonly_fields = ['subtotal']
    raw_id_fields = ['produto']
    
    def subtotal(self, obj):
        return obj.subtotal_formatado
    subtotal.short_description = 'Subtotal'


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    """
    Admin para pedidos
    """
    list_display = ['id', 'cliente', 'status', 'total', 'data_criacao']
    list_filter = ['status', 'data_criacao']
    search_fields = ['cliente__username', 'cliente__email', 'endereco_entrega']
    ordering = ['-data_criacao']
    date_hierarchy = 'data_criacao'
    
    fieldsets = (
        ('Cliente', {
            'fields': ('cliente',)
        }),
        ('Entrega', {
            'fields': ('endereco_entrega', 'observacoes')
        }),
        ('Status e Total', {
            'fields': ('status', 'total')
        }),
    )
    
    inlines = [ItemPedidoInline]
    raw_id_fields = ['cliente']
    readonly_fields = ['total']
    list_editable = ['status']


@admin.register(ItemPedido)
class ItemPedidoAdmin(admin.ModelAdmin):
    """
    Admin para itens de pedido
    """
    list_display = ['pedido', 'produto', 'quantidade', 'preco_unitario', 'subtotal_formatado']
    list_filter = ['pedido__status']
    search_fields = ['produto__nome', 'pedido__cliente__username']
    raw_id_fields = ['pedido', 'produto']
