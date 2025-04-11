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
from .models import Profile
from django.contrib.auth.models import User

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['cargo', 'pode_cadastrar', 'pode_editar', 'pode_excluir']
        widgets = {
            'cargo': forms.Select(attrs={'class': 'form-select'}),
        }

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'email']
