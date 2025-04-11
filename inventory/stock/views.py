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

from django.contrib.auth.views import LoginView
from .forms import CustomLoginForm
class CustomLoginView(LoginView):
    template_name = 'registration/login.html'
    authentication_form = CustomLoginForm

# PODUCTS PAGE
def lista_produtos(request):
    produtos = Produto.objects.all().order_by('categoria')
    return render(request, 'produtos.html', {'produtos': produtos})

# PERFIL PAGE
from django.contrib.auth.decorators import login_required

@login_required
def perfil(request):
    return render(request, 'perfil.html', {'usuario': request.user})

# CADASTRO PAGE
from .forms import ProdutoForm

@login_required
def cadastrar_produto(request):
    if request.method == 'POST':
        form = ProdutoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')  # ou 'produtos' se tiver uma URL assim
    else:
        form = ProdutoForm()
    return render(request, 'cadastrar_produto.html', {'form': form})
