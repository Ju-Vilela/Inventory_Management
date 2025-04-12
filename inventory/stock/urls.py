from django.urls import path
from . import views

app_name = 'stock'

urlpatterns = [
    path('', views.home, name='home'),
    path('produtos/<int:product_id>/editar/', views.edit_product, name='edit_product'),
    path('produtos/<int:product_id>/excluir/', views.delete_product, name='delete_product'),
]
