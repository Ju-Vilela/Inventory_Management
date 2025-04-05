from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import Product

@login_required
def home(request):
    produtos = Product.objects.all()
    return render(request, 'home.html')
