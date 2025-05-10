import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone
from djmoney.models.fields import MoneyField


# CUSTOMUSER
from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ADMIN = 'admin'
    VENDEDOR = 'vendedor'
    GERENTE = 'gerente'

    CARGOS = [
        (ADMIN, 'Admin'),
        (VENDEDOR, 'vendedor'),
        (GERENTE, 'Gerente'),
    ]

    cargo = models.CharField(
        max_length=50,
        choices=CARGOS,
        default=VENDEDOR,
    )

    @property
    def is_manager(self):
        return self.cargo == 'gerente'
    
    @property
    def is_admin(self):
        return self.cargo == 'admin'

    def save(self, *args, **kwargs):
        if self.is_superuser and self.cargo != self.ADMIN:
            self.cargo = self.ADMIN
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.username

# PRODUTO
class Produto(models.Model):
    item = models.CharField(max_length=100)
    categoria = models.CharField(max_length=100)
    marca = models.CharField(max_length=100, blank=True, default="sem marca")
    estoque = models.IntegerField(default=0, editable=False)
    estoque_minimo = models.PositiveIntegerField(default=0, help_text="Estoque mínimo antes de alerta")
    preco = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    ativo = models.BooleanField(default=True)
    sku = models.CharField(max_length=20, unique=True, blank=True)
    data_cadastro = models.DateTimeField(auto_now_add=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    UNIDADES = [
        ('un', 'Unidade'),
        ('kg', 'Quilograma'),
        ('g', 'Grama'),
        ('l', 'Litro'),
        ('ml', 'Mililitro'),
        ('m', 'Metro'),
        ('cm', 'Centímetro'),
        ('mm', 'Milímetro'),
        ('pc', 'Peça'),
        ('box', 'Caixa'),
        ('pcte', 'Pacote'),
        ('rol', 'Rolo'),
        ('par', 'Par'),
        ('kit', 'Kit'),
        ('cx', 'Caixa'),
        ('saco', 'Saco'),
        ('bandeja', 'Bandeja'),
        ('lata', 'Lata'),
        ('frasco', 'Frasco'),
        ('garrafa', 'Garrafa'),
        ('pacote', 'Pacote')
    ]
    
    unidade_medida = models.CharField(max_length=10, choices=UNIDADES, default='un')

    def save(self, *args, **kwargs):
        if not self.pk and not self.sku:
            prefixo = self.categoria[:3].upper()
            codigo = str(uuid.uuid4().int)[:6]  # Gera 6 dígitos únicos
            self.sku = f"{prefixo}-{codigo}"
        super().save(*args, **kwargs)
    

    def __str__(self):
        return self.item
"""
# MOVIMENTAÇÕES
class MovimentacaoEstoque(models.Model):
    TIPO_CHOICES = [
        ('entrada', 'Entrada'),
        ('saida', 'Saída'),
    ]

    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    validade = models.DateField(null=True, blank=True)
    quantidade = models.IntegerField()
    motivo = models.CharField(max_length=100, blank=True)
    data = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)


    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.tipo == 'entrada':
            self.produto.estoque += self.quantidade
        else:
            self.produto.estoque -= self.quantidade
        self.produto.save()
"""

# ENTRADA
class EntradaEstoque(models.Model):
    TIPOS_ENTRADA = [
        ('compra', 'Compra'),
        ('ajuste', 'Ajuste'),
        ('devolucao', 'Devolução de Cliente'),
        ('transferencia', 'Transferência'),
        ('correcao', 'Correção de Estoque'),
        ('outro', 'Outro'),
    ]

    produto = models.ForeignKey('Produto', on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField()
    data = models.DateTimeField(default=timezone.now)
    validade = models.DateField(null=True, blank=True)
    tipo = models.CharField(max_length=50, choices=TIPOS_ENTRADA, default='compra')
    tipo_personalizado = models.CharField(max_length=100, blank=True, null=True)
    preco_unitario = MoneyField(max_digits=10, decimal_places=2, default_currency='BRL', null=True, blank=True)
    observacoes = models.TextField(blank=True)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    
    def get_tipo_display_personalizado(self):
        return dict(self.TIPOS_ENTRADA).get(self.tipo, self.tipo_personalizado or "Outro")

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:  # só atualiza o estoque se for nova entrada
            self.produto.estoque += self.quantidade
            self.produto.save()


    def __str__(self):
        return f"{self.produto.item} ({self.produto.sku}) - {self.quantidade} un. - {self.get_tipo_display() or 'Tipo não especificado'}"


# HISTORICO
class LogDeAcao(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=20, default='light')
    acao = models.CharField(max_length=50)
    descricao = models.TextField()
    data = models.DateTimeField(auto_now_add=True)
    valor_anterior = models.TextField(null=True, blank=True)
    valor_novo = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.usuario.username} - {self.acao} - {self.data}"
