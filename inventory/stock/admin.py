from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Product

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'first_name', 'last_name', 'email', 'cargo', 'is_manager', 'is_admin']
    list_filter = ['is_manager', 'is_admin']
    search_fields = ['username', 'email']
    ordering = ['username']

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Product)
