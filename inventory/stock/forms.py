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
    NOVA_CATEGORIA_PLACEHOLDER = "Nova categoria (opcional)"

    item = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nome do Item'
        })
    )

    categoria = forms.ChoiceField(
        choices=[],  # preenchido no __init__
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=False
    )

    nova_categoria = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control mt-2',
            'placeholder': NOVA_CATEGORIA_PLACEHOLDER
        })
    )

    marca = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Marca'
        })
    )

    validade = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        })
    )

    vendas = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Vendas'
        })
    )

    estoque = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Estoque'
        })
    )

    preco = forms.DecimalField(
        required=False,
        max_digits=10,
        decimal_places=2,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'R$ 00,00'
        })
    )

    class Meta:
        model = Produto
        fields = '__all__'
        widgets = {
            'ativo': forms.HiddenInput(),
        }

    def clean(self):
        cleaned_data = super().clean()
        categoria = cleaned_data.get('categoria')
        nova_categoria = cleaned_data.get('nova_categoria')

        if not categoria and not nova_categoria:
            raise forms.ValidationError("Você precisa selecionar uma categoria existente ou digitar uma nova.")
        
        if categoria and nova_categoria:
            raise forms.ValidationError("Escolha uma categoria existente **ou** digite uma nova, não os dois.")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        categorias = Produto.objects.values_list('categoria', flat=True).distinct()
        self.fields['categoria'].choices = [('', 'Selecione uma categoria')] + [(c, c) for c in categorias]


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
    senha_atual  = forms.CharField(
        label='Senha Atual',
        widget=forms.PasswordInput(attrs={'class': 'input-field', 'placeholder': 'Senha Atual'})
    )
    nova_senha = forms.CharField(
        label='Nova Senha',
        widget=forms.PasswordInput(attrs={'class': 'input-field', 'placeholder': 'Nova Senha'})
    )
    confirmar_senha = forms.CharField(
        label='Confirmar Senha',
        widget=forms.PasswordInput(attrs={'class': 'input-field', 'placeholder': 'Confirmar Senha'})
    )

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
        widget=forms.PasswordInput(attrs={'class': 'input-field', 'placeholder': 'Senha'}),
        required=False  # Torna o campo senha opcional
    )
    password2 = forms.CharField(
        label='Confirmar Senha',
        widget=forms.PasswordInput(attrs={'class': 'input-field', 'placeholder': 'Confirmar Senha'}),
        required=False  # Torna o campo confirmação de senha opcional
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

        # Se não houver senha preenchida, não validamos
        if not instance or not instance.password:
            del self.fields['password1']
            del self.fields['password2']

        

