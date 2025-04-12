from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import Produto, CustomUser

# LOGIN FORM
class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'input-field', 'placeholder': 'Username'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'input-field', 'placeholder': 'Password'})
    )

# CADASTRO PRODUTO FORM
class ProdutoForm(forms.ModelForm):
    class Meta:
        model = Produto
        fields = ['item', 'categoria', 'marca', 'vendas', 'estoque', 'preco']

# PERFIL FORM
class ProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email', 'cargo']
        labels = {
            'username': 'Usuário',
            'first_name': 'Nome',
            'last_name': 'Sobrenome',
            'email': 'Email',
            'cargo': 'Cargo',
        }

# PASSWORD FORM
class AlterarSenhaForm(forms.Form):
    senha_atual = forms.CharField(widget=forms.PasswordInput(), label="Senha Atual")
    nova_senha = forms.CharField(widget=forms.PasswordInput(), label="Nova Senha")
    confirmar_senha = forms.CharField(widget=forms.PasswordInput(), label="Confirmar Nova Senha")

    def clean(self):
        cleaned_data = super().clean()
        nova = cleaned_data.get("nova_senha")
        confirmar = cleaned_data.get("confirmar_senha")
        if nova and confirmar and nova != confirmar:
            raise forms.ValidationError("As senhas não coincidem.")

# CREATE USUARIO FORM
class UsuarioCreateForm(UserCreationForm):
    cargo = forms.ChoiceField(choices=CustomUser.CARGOS, required=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'cargo', 'password1', 'password2']
