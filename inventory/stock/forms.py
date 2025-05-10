from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import EntradaEstoque, Produto, CustomUser
from decimal import Decimal
from django.core.exceptions import ValidationError
from djmoney.forms.fields import MoneyField
from decimal import Decimal, InvalidOperation
from django.core.exceptions import ValidationError
import re

# LOGIN FORM
class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'input-field', 'placeholder': 'Username'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'input-field', 'placeholder': 'Password'})
    )

# FORMULÁRIO DE CADASTRO DE PRODUTO
class ProdutoForm(forms.ModelForm):
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
            'placeholder': "Nova categoria (opcional)"
        })
    )

    marca = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Marca'
        })
    )
 
    estoque_minimo = forms.IntegerField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Estoque Mínimo'
        }),
        label="Estoque Mínimo"
    )

    preco = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Preço',
            'step': '0.01'
        })
    )

    unidade_medida = forms.ChoiceField(
        label='Unidade de Medida',
        choices=Produto.UNIDADES,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'placeholder': 'Unidade de Medida'
        }),
        required=True
    )


    class Meta:
        model = Produto
        fields = '__all__'
        exclude = ['sku']
        widgets = {
            'ativo': forms.HiddenInput(),
        }

    def clean(self):
        cleaned_data = super().clean()
        ativo = cleaned_data.get('ativo')

        if isinstance(ativo, str):
            cleaned_data['ativo'] = ativo.lower() == 'true'
        
        categoria = cleaned_data.get('categoria')
        nova_categoria = cleaned_data.get('nova_categoria')

        if not categoria and not nova_categoria:
            raise forms.ValidationError("Você precisa selecionar uma categoria existente ou digitar uma nova.")
        
        if categoria and nova_categoria:
            raise forms.ValidationError("Escolha uma categoria existente **ou** digite uma nova, não os dois.")
        
        return cleaned_data

    def clean_preco(self):
        preco = self.cleaned_data.get('preco')

        if preco is None:
            return Decimal('0.00')

        if isinstance(preco, str):
            # Remove tudo que não for número ou vírgula/ponto
            preco = re.sub(r'[^\d,.-]', '', preco)
            preco = preco.replace('.', '').replace(',', '.')

        try:
            return Decimal(preco)
        except (ValueError, TypeError, InvalidOperation):
            raise forms.ValidationError("Preço inválido.")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        categorias = Produto.objects.values_list('categoria', flat=True).distinct()
        self.fields['categoria'].choices = [('', 'Selecione uma categoria')] + [(c, c) for c in categorias]

        if not self.is_bound and self.instance and self.instance.pk:
            preco = self.instance.preco
            if preco:
                self.fields['preco'].initial = f"{preco:.2f}".replace('.', ',')

#ENTRADAS
TIPOS_ENTRADA = [
    ('compra', 'Compra'),
    ('ajuste', 'Ajuste'),
    ('devolucao', 'Devolução de cliente'),
    ('transferencia', 'Transferência'),
    ('correcao', 'Correção de estoque'),
    ('outro', 'Outro'),
]
class EntradaEstoqueForm(forms.ModelForm):
    produto = forms.ModelChoiceField(
        queryset=Produto.objects.filter(ativo=True),
        empty_label="Selecione um produto",
        widget=forms.Select(attrs={
            'class': 'form-select',
        }),
        required=True
    )

    tipo = forms.ChoiceField(
        choices=TIPOS_ENTRADA,
        initial='Compra',
        widget=forms.Select(attrs={'class': 'form-select', 'id': 'id_tipo'})
    )

    tipo_personalizado = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control mt-2',
            'placeholder': 'Especifique o tipo'
        })
    )

    validade = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
            'placeholder': 'Validade'
        }),
        label='Data de validade'
    )

    preco_unitario = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '00,00',
            'step': '0.01'
        })
    )

    class Meta:
        model = EntradaEstoque
        fields = ['produto', 'quantidade', 'tipo', 'validade', 'tipo_personalizado', 'preco_unitario', 'observacoes']
        widgets = {
            'quantidade': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Quantidade'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Observações'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        tipo = cleaned_data.get('tipo')
        tipo_personalizado = cleaned_data.get('tipo_personalizado')

        if tipo == 'outro' and not tipo_personalizado:
            self.add_error('tipo_personalizado', 'Por favor, especifique o tipo.')

        return cleaned_data     

    def clean_preco_unitario(self):
        preco_unitario = self.cleaned_data.get('preco_unitario')
        if preco_unitario:
            if isinstance(preco_unitario, str):
                preco_unitario = preco_unitario.replace("R$", "").replace(".", "").replace(",", ".").strip()
            try:
                return Decimal(preco_unitario)
            except (ValueError, TypeError, InvalidOperation):
                raise forms.ValidationError("Preço inválido.")
        return Decimal('0.00')  # se vazio, retorna 0.00


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
            'cargo': 'Cargo', #  Tirar se não tiver permissão ADMIN
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

        
# FORM MONEY
class CustomMoneyField(MoneyField):
    def to_python(self, value):
        if isinstance(value, str):
            value = value.replace('R$', '').replace('.', '').replace(',', '.').strip()
        try:
            value = Decimal(value)
        except (InvalidOperation, ValueError, TypeError):
            raise ValidationError('Preço inválido.')
        return super().to_python(value)
