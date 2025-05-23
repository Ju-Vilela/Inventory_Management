from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login
from django.contrib import messages
from datetime import datetime
from django.utils.timezone import localtime
from .models import Produto, CustomUser, LogDeAcao, ItemSaida, Movimentacao, EntradaEstoque, SaidaEstoque
from .forms import ProdutoForm, ProfileForm, UsuarioCreateForm, AlterarSenhaForm, EntradaEstoqueForm, SaidaForm
from django.contrib.auth import update_session_auth_hash
from django.core.paginator import Paginator
from django.core.serializers.json import DjangoJSONEncoder
import json
from decimal import Decimal


# PERMISSÕES
def tem_permissao_usuario(usuario, permissao):
    return permissao in permissoes_por_cargo.get(usuario.cargo, [])

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
    'vendedor': [
        Permissoes.EDITAR,
        Permissoes.ATUALIZAR_ESTOQUE,
        Permissoes.HISTORICO,
        Permissoes.ALERTAS,
    ],
}

def permissao_necessaria(permissao):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if not tem_permissao_usuario(request.user, permissao):
                messages.error(request, "Você não tem permissão para acessar esta função.", extra_tags='warning')
                return redirect('home')
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

# HISTORICO
def registrar_log(usuario, tipo, acao, descricao, valor_anterior=None, valor_novo=None):
    LogDeAcao.objects.create(
        usuario=usuario,
        tipo=tipo,
        acao=acao,
        descricao=descricao,
        valor_anterior=valor_anterior,
        valor_novo=valor_novo
    )


# HOME PAGE
@login_required
def home(request):
    produtos = Produto.objects.all()
    historico = LogDeAcao.objects.filter(usuario=request.user).order_by('-data')[:50]
    produtos_inativos = Produto.objects.filter(ativo=False)
    produtos_inativos_count = produtos_inativos.count()
    context = {
        'produtos': produtos,
        'historico': historico,
        'timestamp': datetime.now().timestamp(),
        'pode_editar_inativos': tem_permissao_usuario(request.user, Permissoes.ALTERAR_STATUS),
        "show_toast_inativos": request.user.is_staff and produtos_inativos_count > 0,
        'produtos_inativos_count': produtos_inativos_count
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
@permissao_necessaria(Permissoes.ALTERAR_STATUS)
def editar_produto(request, produto_id):
    produto = get_object_or_404(Produto, id=produto_id)
    # Salva os valores antigos antes de instanciar o formulário
    valores_antigos = {}
    for campo in produto._meta.get_fields():
        if not campo.is_relation and campo.name != 'id':  # Ignora o ID e relações
            valores_antigos[campo.name] = getattr(produto, campo.name)

    if request.method == 'POST':
        form = ProdutoForm(request.POST, instance=produto)

        if form.is_valid():
            novo_status = form.cleaned_data.get('ativo')
    
            if form.changed_data and 'ativo' in form.changed_data:
                # Se o status foi alterado, registramos a mudança:
                form.save()
                registrar_log(
                    request.user,
                    'danger' if not novo_status else 'success',
                    "Alteração de Status",
                    f"{produto.item} - {produto.marca}",
                    valor_anterior= {'Status': v for v in valores_antigos.values()},
                    valor_novo={'Status': str(novo_status)}
                )
                if not novo_status:
                    msg = "Produto inativado com sucesso!"  
                    extra_tags='dark'
                else:
                    msg = "Produto reativado com sucesso!"
                    extra_tags='success'
                messages.success(request, msg, extra_tags)
                return redirect('home')
            
            # Após a validação, capturamos os novos valores do formulário
            alteracoes = {}
            for campo in form.changed_data:
                for campo in form.changed_data:
                    if campo == 'sku':
                        continue
                valor_antigo = valores_antigos.get(campo)
                valor_novo = form.cleaned_data[campo]
                alteracoes[campo] = {
                    'antes': str(valor_antigo),
                    'depois': str(valor_novo)
                }
            form.save()

            if alteracoes:
                registrar_log(
                    request.user,
                    'warning',
                    "Edição de Produto",
                    f"{produto.item} - {produto.marca}",
                    valor_anterior={k: v['antes'] for k, v in alteracoes.items()},
                    valor_novo={k: v['depois'] for k, v in alteracoes.items()}
                )

            messages.success(request, "Produto atualizado com sucesso!", extra_tags='success')
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
@permissao_necessaria(Permissoes.ALTERAR_STATUS)
def desativar_produto(request, produto_id):
    produto = get_object_or_404(Produto, id=produto_id)

    if produto.ativo:  
        produto.ativo = False
        produto.save()
        registrar_log(
            request.user,
            'danger',
            "Desativação de Produto",
            f"{produto.item} - {produto.marca}"
        )
        messages.success(request, "Produto desativado com sucesso!")

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
            produto.ativo = True

            nova_categoria = form.cleaned_data.get('nova_categoria')
            categoria = form.cleaned_data.get('categoria')
            produto.categoria = nova_categoria or categoria

            produto.marca = produto.marca or "sem marca"
            produto.preco = produto.preco or 0.00

            produto.save()
            messages.success(request, 'Produto cadastrado com sucesso!', extra_tags='success')
            registrar_log(
                request.user,
                'success',
                "Cadastro de Produto",
                f"{produto.item} - {produto.marca} | {produto.categoria} |  R$ {produto.preco}"
            )
            return redirect('home')
        else:
            if form.errors:
                for field in form:
                    for error in field.errors:
                        messages.error(request, f"Erro ao cadastrar | {field.label} | {error}", extra_tags='danger')
                for error in form.non_field_errors():
                    messages.error(request, error, extra_tags='danger')
                
    else:
        form = ProdutoForm()

    return render(request, 'products.html', {'form': form})

# MOVIMENTAÇÕES
@login_required
@permissao_necessaria(Permissoes.ATUALIZAR_ESTOQUE)
def registrar_entrada(request):
    if request.method == 'POST':
        form = EntradaEstoqueForm(request.POST)
        if form.is_valid():
            entrada = form.save(commit=False)
            entrada.usuario = request.user
            entrada.save()
            messages.success(request, 'Entrada registrada com sucesso!', extra_tags='success')
            registrar_log(
                request.user,
                'success',
                "Cadastro de Entrada",
                f"{entrada.produto} | Qnt. {entrada.quantidade} - Validade: {entrada.validade} | R$ {entrada.preco_unitario} {entrada.observacoes}"
            )
            return redirect('home')
        else:
            for field in form:
                for error in field.errors:
                    messages.error(request, f"Erro | {field.label} | {error}", extra_tags='danger')
            for error in form.non_field_errors():
                messages.error(request, error, extra_tags='danger')
    else:
        form = EntradaEstoqueForm()

    produtos = Produto.objects.filter(ativo=True).values('id', 'sku', 'estoque', 'unidade_medida', 'preco')
    entradas = EntradaEstoque.objects.select_related('produto', 'usuario').order_by('-data')

    for entrada in entradas:
        if entrada.preco_unitario is not None:
            total = entrada.preco_unitario * entrada.quantidade
            entrada.total = total.amount  # só o número
        else:
            entrada.total = 0
    return render(request, 'movimentacao/entradas.html', {
        'form': form,
        'produtos_json': json.dumps(list(produtos), cls=DjangoJSONEncoder),
        'entradas': entradas,
    })


# SAIDA
@login_required
@permissao_necessaria(Permissoes.REGISTRAR_VENDA)
def registrar_saida(request):
    if request.method == 'POST':
        itens_json = request.POST.get('itens_json')
        if not itens_json:
            messages.error(request, "Nenhum item adicionado!")
            return redirect('movimentacao/saidas.html')

        try:
            itens = json.loads(itens_json)
        except json.JSONDecodeError:
            messages.error(request, "Erro ao processar os itens!")
            return redirect('movimentacao/saidas.html')

        form = SaidaForm(request.POST)
        if form.is_valid():
            # Calcula o valor total da saída somando todos os itens
            valor_total = 0
            produtos_objs = {}
            for item in itens:
                produto = Produto.objects.get(id=item['produto_id'])
                quantidade = int(item['quantidade'])
                preco_unitario = item.get('preco_unitario', produto.preco)

                if produto.estoque < quantidade:
                    messages.error(request, f"Estoque insuficiente para o produto {produto.item}!")
                    return redirect('movimentacao/saidas.html')

                valor_total += preco_unitario * quantidade
                produtos_objs[produto.id] = (produto, quantidade, preco_unitario)

            saida = form.save(commit=False)
            saida.itens = itens_json
            saida.quantidade_total = sum([item['quantidade'] for item in itens])
            saida.valor_total = valor_total
            saida.usuario = request.user
            saida.save()

            # Cria os itens da saída e atualiza estoque
            for produto_id, (produto, quantidade, valor) in produtos_objs.items():
                ItemSaida.objects.create(
                    saida=saida,
                    produto=produto,
                    quantidade=quantidade,
                    valor=valor*quantidade
                )
                print(f"Item criado: produto={produto.item}, valor={ItemSaida.valor}")
                # Atualiza estoque
                produto.estoque -= quantidade
                produto.save()

                # Cria movimentação, se tiver esse modelo
                Movimentacao.objects.create(
                    produto=produto,
                    quantidade=quantidade,
                    tipo='Saída',
                    subtipo=saida.tipo,
                    data=saida.data,
                    preco_unitario=valor,
                    observacoes=saida.observacoes,
                    usuario=request.user
                )

            messages.success(request, 'Saída registrada com sucesso!', extra_tags='success')
            produtos_str = ', '.join(
                f"{produto.item} (x{quantidade})"
                for produto, quantidade, _ in produtos_objs.values()
            )
            registrar_log(
                request.user,
                'danger',
                "Cadastro de Saída",
                f"Produtos: {produtos_str}. Valor total: {saida.valor_total}"
            )
            return redirect('home')
        else:
            messages.error(request, "Erro ao salvar o formulário!", extra_tags='danger')
            for field in form:
                for error in field.errors:
                    messages.error(request, f"Erro | {field.label} | {error}", extra_tags='danger')
            for error in form.non_field_errors():
                messages.error(request, error, extra_tags='danger')

    produtos = Produto.objects.filter(ativo=True).values('id', 'item', 'preco', 'estoque')
    context = {
        'form': SaidaForm(),
        'produtos_json': json.dumps(list(produtos), cls=DjangoJSONEncoder),
    }
    return render(request, 'movimentacao/saidas.html', context)

@login_required
def listar_movimentacoes(request):
    entradas = EntradaEstoque.objects.select_related('usuario').prefetch_related('itens_entrada__produto').order_by('-data')
    saidas = SaidaEstoque.objects.select_related('usuario').prefetch_related('itens_saida__produto').order_by('-data')

    context = {
        'entradas': entradas,
        'saidas': saidas,
        'timestamp': datetime.now().timestamp(),
    }
    return render(request, 'movimentacao.html', context)

# PERFIL PAGE
@login_required
def perfil(request):
    user = request.user
    profile_form = ProfileForm(instance=user, mostrar_cargo=False)
    senha_form = AlterarSenhaForm()

    permissoes_usuario = permissoes_por_cargo.get(user.cargo, [])
    historico = LogDeAcao.objects.filter(usuario=request.user).order_by('-data')[:50]

    if request.method == 'POST':
        if 'submit_perfil' in request.POST:
            profile_form = ProfileForm(request.POST, instance=user, mostrar_cargo=False)

            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, 'Dados atualizados com sucesso!', extra_tags='success')
                return redirect('profile')
            else:
                for field in profile_form:
                    for error in field.errors:
                        messages.error(request, f"Erro ao editar alteração | {field.label} | {error}", extra_tags='danger')
                for error in profile_form.non_field_errors():
                    messages.error(request, error, extra_tags='danger')

        elif 'submit_senha' in request.POST:
            senha_atual = request.POST.get('senha_atual')
            nova_senha = request.POST.get('nova_senha')
            confirmar_senha = request.POST.get('confirmar_senha')

            if not user.check_password(senha_atual):
                messages.error(request, 'Senha atual incorreta')
            elif nova_senha != confirmar_senha:
                messages.error(request, 'As senhas novas não coincidem')
            else:
                user.set_password(nova_senha)
                user.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Senha alterada com sucesso!')
                return redirect('profile')

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
            registrar_log(
                request.user,
                'info',
                "Criação de Usuário",
                f"{usuarios.username} - {usuarios.first_name} {usuarios.last_name} | {usuarios.cargo}"
            )
            messages.success(request, 'Usuário criado com sucesso!')
            return redirect('users')
    else:
        form = UsuarioCreateForm()

    return render(request, 'users.html', {'form': form, 'usuarios': usuarios})

# EDITAR USUARIO
def edit_user(request, id):
    usuario = get_object_or_404(CustomUser, id=id)

    valores_antigos = {}
    for campo in usuario._meta.get_fields():
        if not campo.is_relation and campo.name != 'id' and campo.name != 'password':  # Ignora o ID e a senha
            valores_antigos[campo.name] = getattr(usuario, campo.name)

    if request.method == 'POST':
        form = UsuarioCreateForm(request.POST, instance=usuario)
        if form.is_valid():
            alteracoes = {}
            for campo in form.changed_data:
                if campo not in ['password1', 'password2']:
                    valor_antigo = valores_antigos.get(campo)
                    valor_novo = form.cleaned_data[campo]
                    alteracoes[campo] = {
                        'antes': str(valor_antigo),
                        'depois': str(valor_novo)
                    }

            if form.cleaned_data['password1']:
                alteracoes['senha'] = {
                    'antes': "******",
                    'depois': "******"
                }

            form.save()

            if alteracoes:
                registrar_log(
                    request.user,
                    'primary',
                    "Edição de Usuário",
                    f"Usuário: {usuario.username}",
                    valor_anterior={k: v['antes'] for k, v in alteracoes.items()},
                    valor_novo={k: v['depois'] for k, v in alteracoes.items()}
                )

            messages.success(request, "Usuário atualizado com sucesso!")
            return redirect('users')
        else:
            messages.error(request, "Houve um erro ao processar a solicitação.", extra_tags='danger')
    else:
        form = UsuarioCreateForm(instance=usuario)
    

    return render(request, 'editUser.html', {'form': form, 'usuario': usuario})

# DESATIVAR USUARIO
@login_required
def disable_user(request, id):
    usuario = get_object_or_404(CustomUser, id=id)

    if usuario.is_active:
        usuario.is_active = False
        usuario.save()
        registrar_log(
            request.user,
            'dark',
            "Desativação de Usuário",
            f"{usuario.username} - {usuario.first_name} {usuario.last_name} | {usuario.cargo}"
        )
        messages.add_message(request, messages.ERROR, 'Usuário DESATIVADO com sucesso!', extra_tags='dark')
    else:
        messages.error(request, "O usuário já está desativado.")

    return redirect('users')

# ATIVAR USUARIO
def enable_user(request, id):
    usuario = get_object_or_404(CustomUser, id=id)

    if not usuario.is_active:
        usuario.is_active = True
        usuario.save()
        registrar_log(
            request.user,
            'light',
            "Ativação de Usuário",
            f"{usuario.username} - {usuario.first_name} {usuario.last_name} | {usuario.cargo}"
        )
        messages.add_message(request, messages.SUCCESS, 'Usuário ATIVADO com sucesso!', extra_tags='success')

    else:
        messages.warning(request, "Este usuário já está ativo.")

    return redirect('users')
