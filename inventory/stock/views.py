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
from django.contrib.auth.decorators import login_required

@login_required
def perfil(request):
    user = request.user
    profile, created = Profile.objects.get_or_create(user=user)

    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=user)
        profile_form = ProfileForm(request.POST, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('perfil')
    else:
        user_form = UserForm(instance=user)
        profile_form = ProfileForm(instance=profile)

    return render(request, 'perfil.html', {
        'usuario': user,
        'user_form': user_form,
        'profile_form': profile_form,
        'timestamp': datetime.now().timestamp()
    })
