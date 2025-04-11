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

