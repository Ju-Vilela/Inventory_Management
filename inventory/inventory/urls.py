from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from stock import views
from stock.views import CustomLoginView

urlpatterns = [
    path('', views.home, name='home'), 
    path('admin/', admin.site.urls),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('products/', views.lista_produtos, name='productsList'),
    path('perfil/', views.perfil, name='profile'),
    path('usuarios/', views.lista_usuarios, name='users'),
    path('usuarios/adicionar/', views.addUser, name='addUser'),
    path('cadastrar/', views.cadastrar_produto, name='products'),
    
]

from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
