"""
Formulários do app Contas
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario


class RegistroUsuarioForm(UserCreationForm):
    """
    Formulário de registro de novos usuários
    """
    
    tipo = forms.ChoiceField(
        choices=Usuario.TipoUsuario.choices,
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input'
        }),
        label='Tipo de Conta'
    )
    
    class Meta:
        model = Usuario
        fields = [
            'username', 
            'email', 
            'first_name', 
            'last_name', 
            'tipo',
            'telefone',
            'password1', 
            'password2'
        ]
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome de usuário'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'seu@email.com'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Primeiro nome'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Sobrenome'
            }),
            'telefone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+244 9XX XXX XXX'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Senha'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirme a senha'
        })
        self.fields['email'].required = True


class PerfilUsuarioForm(forms.ModelForm):
    """
    Formulário de edição de perfil
    """
    
    class Meta:
        model = Usuario
        fields = [
            'first_name',
            'last_name',
            'email',
            'telefone',
            'endereco',
            'cidade',
            'provincia',
            'foto_perfil',
            'descricao',
            'nome_empresa',
            'nif',
            'area_cultivo',
            'tipos_cultivo',
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control'
            }),
            'telefone': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'endereco': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'cidade': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'provincia': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'foto_perfil': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'descricao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4
            }),
            'nome_empresa': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'nif': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'area_cultivo': forms.NumberInput(attrs={
                'class': 'form-control'
            }),
            'tipos_cultivo': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
        }
