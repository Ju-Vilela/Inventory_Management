from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from stock import views
from stock.views import login_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('stock.urls')),
    path('login/', login_view, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),

    path('catalogo-produtos/', views.catalogo, name='catalogo'),
    path('cadastrar-produto/', views.cadastrar_produto, name='products'),
    path('produtos/<int:produto_id>/editar/', views.editar_produto, name='editProduct'),

    path('perfil/', views.perfil, name='profile'),
    path('usuarios/', views.users, name='users'),
    path('usuarios/adicionar-usuario/',  views.add_user, name='addUser'),
    path('usuarios/edit/<int:id>/', views.edit_user, name='editUser'),
    path('usuarios/disable/<int:id>/', views.disable_user, name='disableUser'),
    path('usuarios/ativar/<int:id>/', views.enable_user, name='enableUser'),
    
    path('movimentacao-entrada/', views.registrar_entrada, name='entradas'),
    path('movimentacao-saida/', views.registrar_saida, name='saidas'),
    path('movimentacoes/', views.listar_movimentacoes, name='movimentacoes'),

    path('', views.home, name='home'),
]


from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
