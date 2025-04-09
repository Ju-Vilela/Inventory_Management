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
    path('products/', views.lista_produtos, name='products'),
]
