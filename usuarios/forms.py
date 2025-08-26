from django import forms
from .models import Usuario

class UsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['nome', 'email', 'senha', 'foto', 'tipo']
        
        widgets = {
            'senha': forms.PasswordInput(attrs={
                'class': 'form-control',
                'placeholder': 'Digite sua senha'
            }),
            'nome': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Digite o nome completo'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Digite o email'
            }),
            'foto': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'tipo': forms.Select(attrs={
                'class': 'form-control'
            })
        }
        
        labels = {
            'nome': 'Nome Completo',
            'email': 'E-mail',
            'senha': 'Senha',
            'foto': 'Foto de Perfil',
            'tipo': 'Tipo de Usuário'
        }
        
        help_texts = {
            'tipo': 'Administrador: Acesso total. Gerente: Pode criar subcontas. Usuário: Acesso limitado.',
            'foto': 'Formatos aceitos: JPG, PNG, GIF (máximo 5MB)'
        }


class LoginForm(forms.Form):
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite seu email'
        }),
        label='E-mail'
    )
    senha = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite sua senha'
        }),
        label='Senha'
    )


class AlterarSenhaForm(forms.Form):
    senha_atual = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite sua senha atual'
        }),
        label='Senha Atual'
    )
    nova_senha = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite a nova senha'
        }),
        label='Nova Senha'
    )
    confirmar_senha = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirme a nova senha'
        }),
        label='Confirmar Nova Senha'
    )
    
    def clean(self):
        cleaned_data = super().clean()
        nova_senha = cleaned_data.get('nova_senha')
        confirmar_senha = cleaned_data.get('confirmar_senha')
        
        if nova_senha and confirmar_senha:
            if nova_senha != confirmar_senha:
                raise forms.ValidationError('As senhas não coincidem.')
        
        return cleaned_data


class CriarAdminInicialForm(forms.Form):
    nome = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite o nome do administrador'
        }),
        label='Nome do Administrador'
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite o email do administrador'
        }),
        label='E-mail do Administrador'
    )
    senha = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Digite a senha do administrador'
        }),
        label='Senha do Administrador'
    )
    confirmar_senha = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirme a senha do administrador'
        }),
        label='Confirmar Senha'
    )
    
    def clean(self):
        cleaned_data = super().clean()
        senha = cleaned_data.get('senha')
        confirmar_senha = cleaned_data.get('confirmar_senha')
        
        if senha and confirmar_senha:
            if senha != confirmar_senha:
                raise forms.ValidationError('As senhas não coincidem.')
        
        return cleaned_data


class FiltroUsuarioForm(forms.Form):
    TIPO_CHOICES = [
        ('', 'Todos os tipos'),
        ('admin', 'Administrador'),
        ('gerente', 'Gerente'),
        ('usuario', 'Usuário'),
    ]
    
    tipo = forms.ChoiceField(
        choices=TIPO_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label='Filtrar por Tipo'
    )
    
    nome = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por nome...'
        }),
        label='Buscar por Nome'
    )
    
    email = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por email...'
        }),
        label='Buscar por Email'
    )
        