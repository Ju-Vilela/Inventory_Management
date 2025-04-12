from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login
from django.contrib import messages
from datetime import datetime
from django.utils.timezone import localtime
from .models import Produto, CustomUser, LogDeAcao, Product
from .forms import ProdutoForm, ProfileForm, UsuarioCreateForm, AlterarSenhaForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.hashers import check_password


# HOME PAGE
@login_required
def home(request):
    produtos = Produto.objects.all()
    context = {
        'produtos': produtos,
        'timestamp': datetime.now().timestamp()
    }
    return render(request, 'home.html', context)

# LOGIN PAGE
def login_view(request):
    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)
        return redirect('home')
    return render(request, 'registration/login.html', {'form': form})

# PRODUCTS LIST
@login_required
def lista_produtos(request):
    produtos = Produto.objects.all().order_by('categoria')
    context = {
        'produtos': produtos,
        'timestamp': datetime.now().timestamp()
    }
    return render(request, 'productsList.html', context)

# CADASTRO PAGE
@login_required
def cadastrar_produto(request):
    if request.method == 'POST':
        form = ProdutoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = ProdutoForm()
    return render(request, 'products.html', {'form': form})

# PERFIL PAGE
@login_required
def perfil(request):
    user = request.user
    profile_form = ProfileForm(instance=user)
    senha_form = AlterarSenhaForm()

    if request.method == 'POST':
        if 'submit_perfil' in request.POST:
            profile_form = ProfileForm(request.POST, instance=user)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, 'Perfil atualizado com sucesso.')
                return redirect('profile')

        elif 'submit_senha' in request.POST:
            senha_form = AlterarSenhaForm(request.POST)
            if senha_form.is_valid():
                senha_atual = senha_form.cleaned_data['senha_atual']
                nova_senha = senha_form.cleaned_data['nova_senha']

                if check_password(senha_atual, user.password):
                    user.set_password(nova_senha)
                    user.save()
                    update_session_auth_hash(request, user)
                    messages.success(request, 'Senha alterada com sucesso.')
                    return redirect('profile')
                else:
                    senha_form.add_error('senha_atual', 'Senha atual incorreta.')


    class Permissoes:
        ACESSO_TOTAL = 'Acesso Total'
        GESTAO_PRODUTOS = 'Gestão de Produtos'
        GESTAO_USUARIOS = 'Gestão de Usuários'
        CONFIG_USUARIOS = 'Configurações de Usuários'
        CADASTRAR = 'Cadastrar produtos'
        EDITAR = 'Editar produtos'
        ATUALIZAR_ESTOQUE = 'Atualizar estoque'
        REGISTRAR_VENDA = 'Registrar venda'
        ALTERAR_STATUS = 'Alterar status (ativo/inativo)'
        HISTORICO = 'Ver histórico'
        ALERTAS = 'Receber alertas'

    permissoes_por_cargo = {
        'admin': [
            Permissoes.ACESSO_TOTAL,
            Permissoes.GESTAO_PRODUTOS,
            Permissoes.GESTAO_USUARIOS,
            Permissoes.CONFIG_USUARIOS,
            Permissoes.CADASTRAR,
            Permissoes.EDITAR,
            Permissoes.ATUALIZAR_ESTOQUE,
            Permissoes.REGISTRAR_VENDA,
            Permissoes.ALTERAR_STATUS,
            Permissoes.HISTORICO,
            Permissoes.ALERTAS,
        ],
        'gerente': [
            Permissoes.ACESSO_TOTAL,
            Permissoes.GESTAO_USUARIOS,
            Permissoes.CADASTRAR,
            Permissoes.EDITAR,
            Permissoes.ATUALIZAR_ESTOQUE,
            Permissoes.REGISTRAR_VENDA,
            Permissoes.ALTERAR_STATUS,
            Permissoes.HISTORICO,
            Permissoes.ALERTAS,
        ],
        'funcionario': [
            Permissoes.EDITAR,
            Permissoes.ATUALIZAR_ESTOQUE,
            Permissoes.HISTORICO,
            Permissoes.ALERTAS,
        ],
    }

    permissoes_usuario = permissoes_por_cargo.get(user.cargo, [])
    historico = LogDeAcao.objects.filter(usuario=user).order_by('-data')[:10]

    if request.method == 'POST':
        profile_form = ProfileForm(request.POST, instance=user)

        senha_atual = request.POST.get('senha_atual')
        nova_senha = request.POST.get('nova_senha')
        confirmar_senha = request.POST.get('confirmar_senha')

        if profile_form.is_valid():
            profile_form.save()
            messages.success(request, 'Dados atualizados com sucesso!')

        # Lógica para alterar a senha
        if senha_atual or nova_senha or confirmar_senha:
            if not user.check_password(senha_atual):
                messages.error(request, 'Senha atual incorreta')
            elif nova_senha != confirmar_senha:
                messages.error(request, 'As senhas novas não coincidem')
            else:
                user.set_password(nova_senha)
                user.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Senha alterada com sucesso!')

        return redirect('perfil')

    else:
        profile_form = ProfileForm(instance=user)

    context = {
        'profile_form': profile_form,
        'usuario': user,
        'senha_form': senha_form,
        'historico': historico,
        'timestamp': datetime.now().timestamp(),
        'ultimo_login': localtime(user.last_login),
        'data_criacao': localtime(user.date_joined),
        'permissoes': permissoes_usuario,
    }

    return render(request, 'profile.html', context)



# ADMIN PAGE
def is_admin(user):
    return user.cargo in ['admin', 'dono']

@login_required
def lista_usuarios(request):
    if not is_admin(request.user):
        return redirect('home')
    
    usuarios = CustomUser.objects.all()
    return render(request, 'users.html', {'users': usuarios})

# CRIAR USUARIO
def add_user(request):
    usuarios = CustomUser.objects.all()
    if request.method == 'POST':
        form = UsuarioCreateForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('users')
    else:
        form = UsuarioCreateForm()

    return render(request, 'users.html', {'form': form, 'users': usuarios})


# PERMISSÕES
@login_required
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if not product.can_edit(request.user):
        messages.error(request, "Você não tem permissão para editar este produto.")
        return redirect('home')  # Ou outra página apropriada

    if request.method == 'POST':
        product.name = request.POST.get('name')
        product.description = request.POST.get('description')
        product.quantity = request.POST.get('quantity')
        product.price = request.POST.get('price')
        product.save()
        return redirect('product_list')
    
    return render(request, 'edit_product.html', {'product': product})

@login_required
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if not product.can_delete(request.user):
        messages.error(request, "Você não tem permissão para excluir este produto.")
        return redirect('home')  # Ou outra página apropriada

    product.delete()
    return redirect('product_list')
