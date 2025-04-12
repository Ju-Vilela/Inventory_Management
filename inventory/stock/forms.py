from django import forms
from django.contrib.auth.forms import AuthenticationForm

# LOGIN FORM
class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'input-field', 'placeholder': 'Username'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'input-field', 'placeholder': 'Password'})
    )

# CADASTRO FORM
from .models import Produto

class ProdutoForm(forms.ModelForm):
    class Meta:
        model = Produto
        fields = ['item', 'categoria', 'marca', 'vendas', 'estoque', 'preco']

# PERFIL FORM
from django.contrib.auth.models import User
from .models import Profile

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        labels = {
            'first_name': 'Nome',
            'last_name': 'Sobrenome',
            'email': 'Email',
        }

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['cargo', 'pode_cadastrar', 'pode_editar', 'pode_excluir']
        labels = {
            'cargo': 'Cargo',
            'pode_cadastrar': 'Pode cadastrar produtos?',
            'pode_editar': 'Pode editar produtos?',
            'pode_excluir': 'Pode excluir produtos?',
        }

# CREATE FORM
from django.contrib.auth.forms import UserCreationForm
from .models import User

class UsuarioCreateForm(UserCreationForm):
    cargo = forms.ChoiceField(choices=User.CARGOS, required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'cargo', 'password1', 'password2']
