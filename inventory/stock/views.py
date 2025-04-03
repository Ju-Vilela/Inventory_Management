from django.shortcuts import render
from .models import Product

def home(request):
    produtos = Product.objects.all()
    return render(request, 'stock/home.html', {'produtos': produtos})
