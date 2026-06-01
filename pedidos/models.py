"""
Modelos do app Pedidos - Carrinho, pedidos, notificações e avaliações
"""

from django.db import models
from django.conf import settings
from produtos.models import Produto


class Pedido(models.Model):
    """
    Pedidos realizados pelos produtores
    """
    
    class StatusPedido(models.TextChoices):
        PENDENTE = 'PENDENTE', 'Pendente'
        CONFIRMADO = 'CONFIRMADO', 'Confirmado'
        EM_PREPARACAO = 'EM_PREPARACAO', 'Em Preparação'
        ENVIADO = 'ENVIADO', 'Enviado'
        ENTREGUE = 'ENTREGUE', 'Entregue'
        CANCELADO = 'CANCELADO', 'Cancelado'
    
    cliente = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='pedidos',
        verbose_name='Cliente'
    )
    status = models.CharField(
        max_length=20,
        choices=StatusPedido.choices,
        default=StatusPedido.PENDENTE,
        verbose_name='Status'
    )
    # Campo para controlar confirmação de entrega pelo produtor
    entrega_confirmada = models.BooleanField(
        default=False,
        verbose_name='Entrega Confirmada pelo Produtor'
    )
    endereco_entrega = models.TextField(
        verbose_name='Endereço de Entrega'
    )
    observacoes = models.TextField(
        blank=True,
        verbose_name='Observações'
    )
    total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name='Total'
    )
    data_criacao = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Data do Pedido'
    )
    data_atualizacao = models.DateTimeField(
        auto_now=True,
        verbose_name='Última Atualização'
    )
    
    class Meta:
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'
        ordering = ['-data_criacao']
    
    def __str__(self):
        return f"Pedido #{self.pk} - {self.cliente.username}"
    
    @property
    def total_formatado(self):
        return f"Kz {self.total:,.2f}"
    
    def calcular_total(self):
        total = sum(item.subtotal for item in self.itens.all())
        self.total = total
        self.save()
        return total


class ItemPedido(models.Model):
    """
    Itens dentro de um pedido
    """
    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        related_name='itens',
        verbose_name='Pedido'
    )
    produto = models.ForeignKey(
        Produto,
        on_delete=models.CASCADE,
        verbose_name='Produto'
    )
    quantidade = models.PositiveIntegerField(
        default=1,
        verbose_name='Quantidade'
    )
    preco_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Preço Unitário'
    )
    
    class Meta:
        verbose_name = 'Item do Pedido'
        verbose_name_plural = 'Itens do Pedido'
    
    def __str__(self):
        return f"{self.quantidade}x {self.produto.nome}"
    
    @property
    def subtotal(self):
        return self.quantidade * self.preco_unitario
    
    @property
    def subtotal_formatado(self):
        return f"Kz {self.subtotal:,.2f}"
    
    def save(self, *args, **kwargs):
        if not self.preco_unitario:
            self.preco_unitario = self.produto.preco
        super().save(*args, **kwargs)


class Notificacao(models.Model):
    """
    Notificações enviadas ao produtor sobre o estado dos seus pedidos
    """
    
    class TipoNotificacao(models.TextChoices):
        STATUS_ATUALIZADO = 'STATUS_ATUALIZADO', 'Status Atualizado'
        ENTREGUE = 'ENTREGUE', 'Pedido Entregue - Confirmar'
        AVALIACAO = 'AVALIACAO', 'Avaliação Recebida'
    
    destinatario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notificacoes',
        verbose_name='Destinatário'
    )
    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        related_name='notificacoes',
        verbose_name='Pedido'
    )
    tipo = models.CharField(
        max_length=30,
        choices=TipoNotificacao.choices,
        default=TipoNotificacao.STATUS_ATUALIZADO,
        verbose_name='Tipo'
    )
    mensagem = models.TextField(verbose_name='Mensagem')
    lida = models.BooleanField(default=False, verbose_name='Lida')
    data_criacao = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Notificação'
        verbose_name_plural = 'Notificações'
        ordering = ['-data_criacao']
    
    def __str__(self):
        return f"Notif para {self.destinatario.username} - Pedido #{self.pedido.pk}"


class AvaliacaoProduto(models.Model):
    """
    Avaliações feitas pelos produtores após receber o produto
    """
    
    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        related_name='avaliacoes',
        verbose_name='Pedido'
    )
    produto = models.ForeignKey(
        Produto,
        on_delete=models.CASCADE,
        related_name='avaliacoes',
        verbose_name='Produto'
    )
    avaliador = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='avaliacoes_feitas',
        verbose_name='Avaliador'
    )
    nota = models.PositiveSmallIntegerField(
        choices=[(i, f'{i} estrela{"s" if i > 1 else ""}') for i in range(1, 6)],
        verbose_name='Nota'
    )
    comentario = models.TextField(blank=True, verbose_name='Comentário')
    data_criacao = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Avaliação'
        verbose_name_plural = 'Avaliações'
        unique_together = [['pedido', 'produto', 'avaliador']]
        ordering = ['-data_criacao']
    
    def __str__(self):
        return f"Avaliação de {self.avaliador.username} - {self.produto.nome} ({self.nota}★)"
