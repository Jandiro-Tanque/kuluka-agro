"""
Formulários do app Produtos
"""

from django import forms
from .models import Produto, Categoria


class ProdutoForm(forms.ModelForm):
    """
    Formulário para criar/editar produtos
    """
    
    class Meta:
        model = Produto
        fields = [
            'nome',
            'categoria',
            'descricao',
            'preco',
            'unidade_medida',
            'estoque',
            'imagem',
            'ativo',
            'destaque',
        ]
        widgets = {
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome do produto'
            }),
            'categoria': forms.Select(attrs={
                'class': 'form-select'
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Descrição detalhada do produto'
            }),
            'preco': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0.00',
                'step': '0.01'
            }),
            'unidade_medida': forms.Select(attrs={
                'class': 'form-select'
            }),
            'estoque': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': '0'
            }),
            'imagem': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'ativo': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'destaque': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
