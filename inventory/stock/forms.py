from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import EntradaEstoque, SaidaEstoque, Produto, CustomUser
from decimal import Decimal
from django.core.exceptions import ValidationError
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
        required=True,
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

# MOVIMENTAÇÃO DE ESTOQUE
class EntradaEstoqueForm(forms.ModelForm):
    produto = forms.ModelChoiceField(
        queryset=Produto.objects.filter(ativo=True).order_by('item'),
        empty_label="Selecione um produto",
        widget=forms.Select(attrs={'class': 'form-select2 form-select'}),
    )

    tipo = forms.ChoiceField(
        choices=EntradaEstoque.TIPOS_ENTRADA,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )

    tipo_personalizado = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Especifique o tipo'
        }),
        label="Outro tipo"
    )

    validade = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        label='Validade',
    )

    preco_unitario = forms.DecimalField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control text-start',
            'placeholder': 'R$ 0,00',
            'data-mask': '000.000.000,00',
            'data-inputmask-unmaskasnumber': 'true',
        }),
        max_digits=10, decimal_places=2,
        label='Preço Unitário'
    )

    class Meta:
        model = EntradaEstoque
        fields = ['produto', 'quantidade', 'tipo', 'validade', 'preco_unitario', 'observacoes']
        widgets = {
            'quantidade': forms.NumberInput(attrs={'class': 'form-control'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def clean(self):
        cleaned_data = super().clean()
        tipo = cleaned_data.get("tipo")
        tipo_personalizado = cleaned_data.get("tipo_personalizado")

        if tipo == "Outro" and tipo_personalizado:
            cleaned_data["tipo"] = tipo_personalizado  # Substitui pelo valor digitado
        elif tipo == "Outro" and not tipo_personalizado:
            self.add_error("tipo_personalizado", "Por favor, informe um tipo personalizado.")

        return cleaned_data  

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        preco_unitario = self.data.get('preco_unitario')
        if preco_unitario:
            try:
                self.data = self.data.copy()
                preco_unitario = preco_unitario.replace("R$", "").replace(".", "").replace(",", ".").strip()
                self.data['preco_unitario'] = str(Decimal(preco_unitario))
            except (InvalidOperation, ValueError):
                pass

# SAIDA FORM
class SaidaForm(forms.ModelForm):
    # Campo auxiliar para adicionar produtos à lista (não será salvo diretamente)
    produto = forms.ModelChoiceField(
        queryset=Produto.objects.filter(ativo=True).order_by('item'),
        empty_label="Selecione um produto",
        widget=forms.Select(attrs={'class': 'form-select2 form-select'}),
        required=False,
    )

    quantidade_individual = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Quantidade'}),
        label="Quantidade"
    )

    valor_unitario = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'readonly': 'readonly',
            'placeholder': 'R$ 0,00'
        }),
        label='Preço Unitário',
        max_digits=10,
        decimal_places=2,
    )

    tipo = forms.ChoiceField(
        choices=SaidaEstoque.TIPOS_SAIDA,
        widget=forms.Select(attrs={'class': 'form-select'}),
    )

    tipo_personalizado = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Especifique o tipo'
        }),
        label="Outro tipo"
    )

    class Meta:
        model = SaidaEstoque
        fields = ['tipo', 'observacoes']
        widgets = {
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }

    def clean(self):
        cleaned_data = super().clean()
        tipo = cleaned_data.get("tipo")
        tipo_personalizado = cleaned_data.get("tipo_personalizado")

        if tipo == "Outro" and tipo_personalizado:
            cleaned_data["tipo"] = tipo_personalizado
        elif tipo == "Outro" and not tipo_personalizado:
            self.add_error("tipo_personalizado", "Por favor, informe um tipo personalizado.")

        return cleaned_data



# PERFIL FORM
class ProfileForm(forms.ModelForm):
    def __init__(self, *args, mostrar_cargo=True, **kwargs):
        super().__init__(*args, **kwargs)
        if not mostrar_cargo:
            self.fields.pop('cargo')

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
        instance = kwargs.get('instance', None)
        super().__init__(*args, **kwargs)

        if instance:
            # Remover username ao editar
            del self.fields['username']
        else:
            # Ao criar usuário, senha é obrigatória
            self.fields['password1'].required = True
            self.fields['password2'].required = True

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password1')
        if password:
            user.set_password(password)
        if commit:
            user.save()
        return user

