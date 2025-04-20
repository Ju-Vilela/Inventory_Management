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

from django import forms
from .models import Produto

# FORMULÁRIO DE CADASTRO DE PRODUTO
class ProdutoForm(forms.ModelForm):
    item = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Item'})
    )
    categoria = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Categoria'})
    )
    marca = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Marca'})
    )
    validade = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    vendas = forms.IntegerField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0'})
    )
    estoque = forms.IntegerField(
        required=True,
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0'})
    )
    preco = forms.DecimalField(
        required=True,
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '00,00'})
    )

    class Meta:
        model = Produto
        fields = ['item', 'categoria', 'marca', 'validade', 'vendas', 'estoque', 'preco']


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
    cargo = forms.ChoiceField(
        choices=CustomUser.CARGOS,
        required=True,
        widget=forms.Select(attrs={'class': 'input-field'})
    )

    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'input-field', 'placeholder': 'Usuário'}),
        required=True
    )
    first_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'input-field', 'placeholder': 'Nome'})
    )
    last_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'input-field', 'placeholder': 'Sobrenome'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'input-field', 'placeholder': 'Email'})
    )
    password1 = forms.CharField(
        label='Senha',
        widget=forms.PasswordInput(attrs={'class': 'input-field', 'placeholder': 'Senha'})
    )
    password2 = forms.CharField(
        label='Confirmar Senha',
        widget=forms.PasswordInput(attrs={'class': 'input-field', 'placeholder': 'Confirmar Senha'})
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email', 'cargo', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        # Se o formulário não estiver sendo passado com uma instância de usuário (edição), mostramos o campo 'username'
        instance = kwargs.get('instance', None)
        super().__init__(*args, **kwargs)

        if instance:
            # Se for edição (com instância de usuário), podemos remover o campo 'username'
            del self.fields['username']

        

