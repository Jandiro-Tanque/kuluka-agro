"""
Modelos do app Contas - Gerenciamento de usuários
"""

from django.db import models
from django.contrib.auth.models import AbstractUser


class Usuario(AbstractUser):
    """
    Modelo de usuário customizado com tipos: Fornecedor ou Produtor
    """
    
    class TipoUsuario(models.TextChoices):
        FORNECEDOR = 'FORNECEDOR', 'Fornecedor'
        PRODUTOR = 'PRODUTOR', 'Produtor'
    
    tipo = models.CharField(
        max_length=20,
        choices=TipoUsuario.choices,
        default=TipoUsuario.PRODUTOR,
        verbose_name='Tipo de Usuário'
    )
    telefone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Telefone'
    )
    endereco = models.TextField(
        blank=True,
        verbose_name='Endereço'
    )
    cidade = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Cidade'
    )
    provincia = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Província'
    )
    foto_perfil = models.ImageField(
        upload_to='perfis/',
        blank=True,
        null=True,
        verbose_name='Foto de Perfil'
    )
    descricao = models.TextField(
        blank=True,
        verbose_name='Descrição / Sobre'
    )
    data_criacao = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Data de Criação'
    )
    
    # Campos específicos para Fornecedor
    nome_empresa = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Nome da Empresa'
    )
    nif = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='NIF (Número de Identificação Fiscal)'
    )
    
    # Campos específicos para Produtor
    area_cultivo = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name='Área de Cultivo (hectares)'
    )
    tipos_cultivo = models.TextField(
        blank=True,
        verbose_name='Tipos de Cultivo'
    )
    
    class Meta:
        verbose_name = 'Usuário'
        verbose_name_plural = 'Usuários'
    
    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_tipo_display()})"
    
    @property
    def eh_fornecedor(self):
        return self.tipo == self.TipoUsuario.FORNECEDOR
    
    @property
    def eh_produtor(self):
        return self.tipo == self.TipoUsuario.PRODUTOR
