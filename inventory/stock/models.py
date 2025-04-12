from django.db import models

class Produto(models.Model):
    item = models.CharField(max_length=100)
    categoria = models.CharField(max_length=100)
    marca = models.CharField(max_length=100)
    validade = models.DateField(null=True, blank=True)
    vendas = models.IntegerField(default=0)
    estoque = models.IntegerField()
    preco = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.item

from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    cargo = models.CharField(max_length=30, choices=[
        ('dono', 'Dono'),
        ('admin', 'Administrador'),
        ('funcionario', 'Funcionário')
    ])
    pode_cadastrar = models.BooleanField(default=False)
    pode_editar = models.BooleanField(default=False)
    pode_excluir = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} ({self.cargo})"

# sempre que um usuário novo for criado, o Profile dele também sera automaticamente gerado.
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def criar_ou_atualizar_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        instance.profile.save()

# HISTORICO
from django.contrib.auth.models import User

class LogDeAcao(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    acao = models.CharField(max_length=50)
    descricao = models.TextField()
    data = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario.username} - {self.acao} - {self.data}"

# CUSTOMUSER
from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    cargo = models.CharField(max_length=100, null=True, blank=True)
    is_manager = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)

    def __str__(self):
        return self.username

class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    def can_edit(self, user):
        return user.is_admin or user.is_manager

    def can_delete(self, user):
        return user.is_admin


