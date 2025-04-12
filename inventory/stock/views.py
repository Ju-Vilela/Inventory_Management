from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from datetime import datetime
from .models import Produto

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
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login

def login_view(request):
    form = AuthenticationForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)
        return redirect('home')
    return render(request, 'registration/login.html', {'form': form})

# PRODUCTS LIST
from django.contrib.auth.views import LoginView
from .forms import CustomLoginForm

class CustomLoginView(LoginView):
    template_name = 'registration/login.html'
    authentication_form = CustomLoginForm

@login_required
def lista_produtos(request):
    produtos = Produto.objects.all().order_by('categoria')
    context = {
        'produtos': produtos,
        'timestamp': datetime.now().timestamp()
    }
    return render(request, 'productsList.html', context)

# CADASTRO PAGE
from .forms import ProdutoForm

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
from .forms import UserForm, ProfileForm
from django.contrib.auth.models import User
from django.utils.timezone import localtime
from .models import LogDeAcao

@login_required
def perfil(request):
    user = request.user
    profile = user.profile

    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=user)
        profile_form = ProfileForm(request.POST, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('profile')

    else:
        user_form = UserForm(instance=user)
        profile_form = ProfileForm(instance=profile)

    # Aqui pega as ações do usuário (precisa do modelo de histórico)
    historico = LogDeAcao.objects.filter(usuario=user).order_by('-data')[:10]

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'usuario': user,
        'historico': historico,
        'timestamp': datetime.now().timestamp(),
        'ultimo_login': localtime(user.last_login),
        'data_criacao': localtime(user.date_joined)
    }

    return render(request, 'profile.html', context)

# ADMIN PAGE
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User

def is_admin(user):
    return user.profile.cargo in ['admin', 'dono']

@login_required
def lista_usuarios(request):
    if not request.user.is_superuser:
        return redirect('home')

    usuarios = User.objects.all()
    return render(request, 'users.html', {'users': usuarios})

# CRIAR USUARIO
from django.contrib import messages
from .forms import UsuarioCreateForm

def addUser(request):
    if request.method == 'POST':
        form = UsuarioCreateForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuário criado com sucesso!')
            return redirect('usuarios')
        else:
            messages.error(request, 'Erro ao criar usuário. Verifique os campos.')
    else:
        form = UsuarioCreateForm()

    return render(request, 'modal_addUser.html', {'form': form})

# PERMISSÕES
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .models import Product

@login_required
def edit_product(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if not product.can_edit(request.user):
        return HttpResponseForbidden("Você não tem permissão para editar este produto.")

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
        return HttpResponseForbidden("Você não tem permissão para excluir este produto.")

    product.delete()
    return redirect('product_list')
