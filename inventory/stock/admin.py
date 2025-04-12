from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Product

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'cargo', 'is_active', 'date_joined')
    list_filter = ('is_active', 'cargo')

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Product)
