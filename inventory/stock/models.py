import uuid
from django.db import models
from django.conf import settings
from django.utils import timezone
from djmoney.models.fields import MoneyField
from .services import atualizar_estoque
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import JSONField
import json


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
    sku = models.CharField(max_length=30, unique=True, blank=True)
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

    def atualizar_estoque(self, quantidade, tipo='entrada'):
        if tipo == 'entrada':
            self.estoque += quantidade
        elif tipo == 'saida':
            if self.estoque - quantidade < 0:
                raise ValueError("Estoque insuficiente pra essa saída, calma aí!")
            self.estoque -= quantidade
        else:
            raise ValueError("Tipo de movimentação inválido.")
        self.save()

    def save(self, *args, **kwargs):
        if not self.pk and not self.sku:
            prefixo = self.categoria[:3].upper()
            codigo = str(uuid.uuid4().int)[:20]
            self.sku = f"{prefixo}-{codigo}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.item

# MOVIMENTAÇÃO
class Movimentacao(models.Model):
    TIPO_CHOICES = [
        ('Entrada', 'Entrada'),
        ('Saída', 'Saída'),
    ]

    produto = models.ForeignKey('Produto', on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField()
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    subtipo = models.CharField(max_length=30)
    data = models.DateTimeField(default=timezone.now)
    preco_unitario = MoneyField(max_digits=10, decimal_places=2, default_currency='BRL', null=True, blank=True)
    observacoes = models.TextField(blank=True)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    # Referência genérica para EntradaEstoque ou SaidaEstoque
    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    referencia = GenericForeignKey('content_type', 'object_id')

    class Meta:
        ordering = ['-data']

    def __str__(self):
        return f"{self.tipo} de {self.quantidade}x {self.produto.nome}"


# ENTRADA
class EntradaEstoque(models.Model):
    TIPOS_ENTRADA = [
        ('compra', 'Compra'),
        ('ajuste', 'Ajuste de Estoque'),
        ('devolucao', 'Devolução de Cliente'),
        ('transferencia', 'Transferência Recebida'),
        ('correcao', 'Correção Manual'),
        ('outro', 'Outro'),
    ]

    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField()
    validade = models.DateField(null=True, blank=True)
    tipo = models.CharField(max_length=30, choices=TIPOS_ENTRADA)
    preco_unitario = MoneyField(max_digits=10, decimal_places=2, default_currency='BRL', null=True, blank=True)
    data = models.DateTimeField(default=timezone.now)
    observacoes = models.TextField(blank=True)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            atualizar_estoque(self.produto, self.quantidade, 'Entrada')
        super().save(*args, **kwargs)

class ItemEntrada(models.Model):
    entrada = models.ForeignKey('EntradaEstoque', on_delete=models.CASCADE, related_name='itens_entrada')
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField()
    valor = MoneyField(max_digits=10, decimal_places=2, default_currency='BRL', null=True, blank=True)


# SAÍDA
class SaidaEstoque(models.Model):
    TIPOS_SAIDA = [
        ('venda', 'Venda'),
        ('ajuste', 'Ajuste'),
        ('perda', 'Perda'),
        ('transferencia', 'Transferência'),
        ('correcao', 'Correção'),
        ('outro', 'Outro'),
    ]

    itens = models.JSONField(default=list)  # lista de produtos [{id, nome, quantidade, valor_unitario}]
    quantidade_total = models.PositiveIntegerField(default=0)
    valor_total = MoneyField(max_digits=10, decimal_places=2, default_currency='BRL', null=True, blank=True)
    tipo = models.CharField(max_length=30, choices=TIPOS_SAIDA)
    data = models.DateTimeField(default=timezone.now)
    observacoes = models.TextField(blank=True)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f'Saída #{self.pk} - {self.tipo}'
    
    def save(self, *args, **kwargs):
        if not self.pk:
            itens_decodados = json.loads(self.itens)  # transforma string JSON em lista de dicts
            for item in itens_decodados:
                produto_id = item.get('produto_id')  # olha aí, agora funciona!
                quantidade = item.get('quantidade', 0)
                produto = Produto.objects.get(id=produto_id)
                atualizar_estoque(produto, quantidade, 'Saida')
        super().save(*args, **kwargs)


class ItemSaida(models.Model):
    saida = models.ForeignKey('SaidaEstoque', on_delete=models.CASCADE, related_name='itens_saida')
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE)
    quantidade = models.PositiveIntegerField()
    valor = MoneyField(max_digits=10, decimal_places=2, default_currency='BRL', null=True, blank=True)



# HISTORICO
class LogDeAcao(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=50, default='light')
    acao = models.CharField(max_length=50)
    descricao = models.TextField()
    data = models.DateTimeField(auto_now_add=True)
    valor_anterior = models.TextField(null=True, blank=True)
    valor_novo = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.usuario.username} - {self.acao} - {self.data}"
