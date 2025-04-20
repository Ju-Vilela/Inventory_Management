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
from django.core.paginator import Paginator

# PERMISSÕES
def tem_permissao_usuario(usuario, permissao):
    return permissao in permissoes_por_cargo.get(usuario.cargo, [])

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

# EDITAR PRODUTO
@login_required
def editar_produto(request, produto_id):
    produto = get_object_or_404(Produto, id=produto_id)

    if not produto.ativo and not request.user.groups.filter(name='Gerente').exists():
        messages.warning(request, "Você não tem permissão para editar um produto inativo.")
        return redirect('home')

    if request.method == 'POST':
        form = ProdutoForm(request.POST, instance=produto)
        if form.is_valid():
            form.save()
            messages.success(request, "Produto atualizado com sucesso!")
            log = LogDeAcao(
                usuario=request.user,
                acao="Edição de Produto",
                descricao=f"Produto {produto.item} {produto.marca} foi editado com sucesso."
            )
            log.save()
            return redirect('home')
    else:
        form = ProdutoForm(instance=produto)

    context = {
        'form': form,
        'editando': True,
        'produto': produto
    }
    return render(request, 'products.html', context)


# DESATIVAR PRODUTO
@login_required
def desativar_produto(request, produto_id):
    produto = get_object_or_404(Produto, id=produto_id)

    # Verificar se o usuário tem permissão para alterar o status do produto
    if Permissoes.ALTERAR_STATUS not in permissoes_usuario:
        messages.error(request, "Você não tem permissão para alterar o status deste produto.")
        log = LogDeAcao(
            usuario=request.user,
            acao="Usuario sem permissão",
            descricao=f"Tentativa de edição para o Produto: {produto.item} {produto.item} {produto.marca}."
        )
        log.save()
        return redirect('home')

    if produto.ativo:  # Verifica se o produto está ativo antes de desativá-lo
        produto.ativo = False
        produto.save()
        messages.success(request, "Produto desativado com sucesso!")
        log = LogDeAcao(
            usuario=request.user,
            acao="Desativação de Produto",
            descricao=f"Produto {produto.item} {produto.marca} foi desativado com sucesso."
        )
        log.save()

    else:
        messages.warning(request, "Este produto já está desativado.")

    return redirect('home')


# CADASTRO PAGE
@login_required
def cadastrar_produto(request):
    if request.method == 'POST':
        form = ProdutoForm(request.POST)
        if form.is_valid():
            produto = form.save(commit=False)

            nova_categoria = form.cleaned_data.get('nova_categoria')
            categoria = form.cleaned_data.get('categoria')
            produto.categoria = nova_categoria or categoria

            produto.marca = produto.marca or "sem marca"
            produto.vendas = produto.vendas or 0
            produto.estoque = produto.estoque or 0
            produto.preco = produto.preco or 0.00

            produto.save()
            messages.success(request, 'Produto cadastrado com sucesso!', extra_tags='success')
            log = LogDeAcao(
                usuario=request.user,
                acao="Cadastro de Produto",
                descricao=f"Produto {produto.item} {produto.marca} foi cadastrado com sucesso."
            )
            log.save()

            return redirect('home')
        else:
            messages.error(request, 'Erro ao cadastrar produto. Verifique os campos.', extra_tags='danger')
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

    historico = LogDeAcao.objects.filter(usuario=user).order_by('-data')
    
    paginator = Paginator(historico, 10)  # 10 ações por página
    page_number = request.GET.get('page')
    historico_page = paginator.get_page(page_number)

    context = {
        'profile_form': profile_form,
        'usuario': user,
        'senha_form': senha_form,
        'historico': historico,
        'historico': historico_page,
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
    form = UsuarioCreateForm()
    usuarios = CustomUser.objects.all()
    context = {
        'usuarios': usuarios,
        'form': form,
        'timestamp': datetime.now().timestamp()
    }
    return render(request, 'users.html', context)

# USERS PAGE
@login_required
def users(request):
    form = UsuarioCreateForm()
    usuarios = CustomUser.objects.all()
    context = {
        'usuarios': usuarios,
        'form': form,
        'timestamp': datetime.now().timestamp()
    }
    return render(request, 'users.html', context)


# CRIAR USUARIO
def add_user(request):
    usuarios = CustomUser.objects.all()
    if request.method == 'POST':
        form = UsuarioCreateForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuário criado com sucesso!')
            log = LogDeAcao(
                usuario=request.user,
                acao="Ativação de Usuario",
                descricao=f"Usuario {usuarios.username} {usuarios.cargo} foi criado com sucesso."
            )
            log.save()
            return redirect('users')
    else:
        form = UsuarioCreateForm()

    return render(request, 'users.html', {'form': form, 'usuarios': usuarios})

# EDITAR USUARIO
def edit_user(request, id):
    usuario = get_object_or_404(CustomUser, id=id)
    
    if request.method == 'POST':
        form = UsuarioCreateForm(request.POST, instance=usuario)
        if form.is_valid():
            form.save()
            messages.success(request, "Usuário atualizado com sucesso!")
            log = LogDeAcao(
                usuario=request.user,
                acao="Edição de Usuario",
                descricao=f"Usuario {usuario.username} {usuario.cargo} foi editado com sucesso."
            )
            log.save()
            return redirect('users')
    else:
        form = UsuarioCreateForm(instance=usuario)  # Preenche o formulário com os dados do usuário

    return render(request, 'editUser.html', {'form': form, 'usuario': usuario})

# DESATIVAR USUARIO
@login_required
def disable_user(request, id):
    usuario = get_object_or_404(CustomUser, id=id)

    if usuario.is_active:
        usuario.is_active = False
        usuario.save()
        messages.add_message(request, messages.ERROR, 'Usuário DESATIVADO com sucesso!', extra_tags='dark')
        log = LogDeAcao(
            usuario=request.user,
            acao="Desativação de Usuario",
            descricao=f"Usuario {usuario.username} {usuario.cargo} foi desativado com sucesso."
        )
        log.save()
    else:
        messages.error(request, "O usuário já está desativado.")

    return redirect('users')

# ATIVAR USUARIO
def enable_user(request, id):
    usuario = get_object_or_404(CustomUser, id=id)

    if not usuario.is_active:
        usuario.is_active = True
        usuario.save()
        messages.add_message(request, messages.SUCCESS, 'Usuário ATIVADO com sucesso!', extra_tags='success')
        log = LogDeAcao(
            usuario=request.user,
            acao="Ativação de Usuario",
            descricao=f"Usuario {usuario.username} {usuario.cargo} foi ativado com sucesso."
        )
        log.save()

    else:
        messages.warning(request, "Este usuário já está ativo.")

    return redirect('users')
