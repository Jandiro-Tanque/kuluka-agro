"""
Modelos do app Produtos - Catálogo de produtos agrícolas
"""

from django.db import models
from django.conf import settings


class Categoria(models.Model):
    """
    Categorias de produtos agrícolas
    """
    nome = models.CharField(
        max_length=100,
        verbose_name='Nome'
    )
    descricao = models.TextField(
        blank=True,
        verbose_name='Descrição'
    )
    icone = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Ícone (classe Bootstrap)'
    )
    ativo = models.BooleanField(
        default=True,
        verbose_name='Ativo'
    )
    
    class Meta:
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'
        ordering = ['nome']
    
    def __str__(self):
        return self.nome


class Produto(models.Model):
    """
    Produtos oferecidos pelos fornecedores
    """
    
    class UnidadeMedida(models.TextChoices):
        QUILOGRAMA = 'KG', 'Quilograma (kg)'
        GRAMA = 'G', 'Grama (g)'
        TONELADA = 'TON', 'Tonelada (ton)'
        LITRO = 'L', 'Litro (L)'
        UNIDADE = 'UN', 'Unidade (un)'
        SACO = 'SC', 'Saco (sc)'
        CAIXA = 'CX', 'Caixa (cx)'
    
    fornecedor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='produtos',
        verbose_name='Fornecedor'
    )
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='produtos',
        verbose_name='Categoria'
    )
    nome = models.CharField(
        max_length=200,
        verbose_name='Nome do Produto'
    )
    descricao = models.TextField(
        verbose_name='Descrição'
    )
    preco = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Preço'
    )
    unidade_medida = models.CharField(
        max_length=10,
        choices=UnidadeMedida.choices,
        default=UnidadeMedida.QUILOGRAMA,
        verbose_name='Unidade de Medida'
    )
    estoque = models.PositiveIntegerField(
        default=0,
        verbose_name='Estoque Disponível'
    )
    imagem = models.ImageField(
        upload_to='produtos/',
        blank=True,
        null=True,
        verbose_name='Imagem do Produto'
    )
    ativo = models.BooleanField(
        default=True,
        verbose_name='Ativo'
    )
    destaque = models.BooleanField(
        default=False,
        verbose_name='Produto em Destaque'
    )
    data_criacao = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Data de Criação'
    )
    data_atualizacao = models.DateTimeField(
        auto_now=True,
        verbose_name='Última Atualização'
    )
    
    class Meta:
        verbose_name = 'Produto'
        verbose_name_plural = 'Produtos'
        ordering = ['-data_criacao']
    
    def __str__(self):
        return f"{self.nome} - {self.fornecedor.username}"
    
    @property
    def preco_formatado(self):
        return f"Kz {self.preco:,.2f}"
    
    @property
    def disponivel(self):
        return self.ativo and self.estoque > 0
