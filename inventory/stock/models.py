import uuid
import json
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from djmoney.models.fields import MoneyField
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from .utils.codigo_movimentacao import gerar_codigo_movimentacao
from .services import atualizar_estoque

class CustomUser(AbstractUser):
    ADMIN = 'admin'
    VENDEDOR = 'vendedor'
    GERENTE = 'gerente'

    CARGOS = [
        (ADMIN, 'Admin'),
        (VENDEDOR, 'Vendedor'),
        (GERENTE, 'Gerente'),
    ]

    cargo = models.CharField(
        max_length=50,
        choices=CARGOS,
        default=VENDEDOR,
    )

    @property
    def is_manager(self):
        return self.cargo == self.GERENTE

    @property
    def is_admin(self):
        return self.cargo == self.ADMIN

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        from django.contrib.auth.models import Group
        grupo = Group.objects.filter(name=self.cargo).first()
        if grupo:
            self.groups.set([grupo])

    class Meta:
        permissions = [
            ("acesso_total", "Acesso Total"),
            ("gestao_produtos", "Gestão de Produtos"),
            ("gestao_usuarios", "Gestão de Usuários"),
            ("config_usuarios", "Configurações de Usuários"),
            ("cadastrar_produtos", "Cadastrar produtos"),
            ("editar_produtos", "Editar produtos"),
            ("entrada", "Entrada de estoque"),
            ("saida", "Saída de Produtos"),
            ("alterar_status", "Alterar status (ativo/inativo)"),
            ("ver_historico", "Ver histórico"),
            ("receber_alertas", "Receber alertas"),
        ]

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
    

# PRODUTO
class Produto(models.Model):
    item = models.CharField(max_length=100)
    categoria = models.CharField(max_length=100)
    marca = models.CharField(max_length=100, blank=True, default="sem marca")
    estoque = models.PositiveIntegerField(default=0)
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

    @property
    def estoque_atual(self):
        from .services import calcular_estoque_atual
        return calcular_estoque_atual(self.id)

    def save(self, *args, **kwargs):
        if not self.pk and not self.sku:
            prefixo = self.categoria[:3].upper()
            codigo = str(uuid.uuid4().int)[:20]
            self.sku = f"{prefixo}-{codigo}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.item


## MOVIMENTAÇÃO
class Movimentacao(models.Model):
    TIPO_CHOICES = [
        ('Entrada', 'Entrada'),
        ('Saída', 'Saída'),
    ]

    produto = models.ForeignKey('Produto', on_delete=models.CASCADE, null=True, blank=True)
    quantidade = models.PositiveIntegerField()
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    subtipo = models.CharField(max_length=30)
    data = models.DateTimeField(default=timezone.now)
    preco_unitario = MoneyField(max_digits=10, decimal_places=2, default_currency='BRL', null=True, blank=True)
    observacoes = models.TextField(blank=True)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

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
        ('compra',          'Compra'),
        ('ajuste',          'Ajuste de Estoque'),
        ('devolucao',       'Devolução de Cliente'),
        ('transferencia',   'Transferência Recebida'),
        ('correcao',        'Correção Manual'),
        ('outro',           'Outro'),
    ]

    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, null=True, blank=True)
    quantidade = models.PositiveIntegerField(default=0)
    validade = models.DateField(null=True, blank=True)
    tipo = models.CharField(max_length=30, choices=TIPOS_ENTRADA)
    preco_unitario = MoneyField(max_digits=10, decimal_places=2, default_currency='BRL', null=True, blank=True)
    data = models.DateTimeField(default=timezone.now)
    observacoes = models.TextField(blank=True)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    codigo = models.CharField(max_length=30, unique=True, editable=False, blank=True)

    def save(self, *args, **kwargs):
        criando = not self.pk
        super().save(*args, **kwargs)

        if criando and not self.codigo:
            self.codigo = gerar_codigo_movimentacao('entrada', self.tipo, self.pk)
            super().save(update_fields=['codigo'])  # salva apenas o campo novo

        if criando:
            atualizar_estoque(self.produto, self.quantidade, 'Entrada')

class ItemEntrada(models.Model):
    entrada = models.ForeignKey('EntradaEstoque', on_delete=models.CASCADE, related_name='itens_entrada', default="Sem Entrada")
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, null=True, blank=True)
    quantidade = models.PositiveIntegerField(default=0)
    valor = MoneyField(max_digits=10, decimal_places=2, default_currency='BRL', null=True, blank=True)
    codigo = models.CharField(max_length=50, unique=True, editable=False, blank=True)

    def save(self, *args, **kwargs):
        criando = not self.pk
        super().save(*args, **kwargs)
        if criando and not self.codigo:
            self.codigo = f"{self.entrada.codigo}-P{self.produto.pk:04}"
            super().save(update_fields=['codigo'])


# SAÍDA
class SaidaEstoque(models.Model):
    TIPOS_SAIDA = [
        ('venda',           'Venda'),
        ('ajuste',          'Ajuste'),
        ('perda',           'Perda'),
        ('transferencia',   'Transferência'),
        ('correcao',        'Correção'),
        ('outro',           'Outro'),
    ]

    itens = models.JSONField(default=list)  # lista de produtos [{id, nome, quantidade, valor_unitario}]
    quantidade_total = models.PositiveIntegerField(default=0)
    valor_total = MoneyField(max_digits=10, decimal_places=2, default_currency='BRL', null=True, blank=True)
    tipo = models.CharField(max_length=30, choices=TIPOS_SAIDA)
    data = models.DateTimeField(default=timezone.now)
    observacoes = models.TextField(blank=True, default="")
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    codigo = models.CharField(max_length=30, unique=True, editable=False, blank=True)

    def __str__(self):
        return f'Saída #{self.pk} - {self.tipo}'
    
    def save(self, *args, **kwargs):
        criando = not self.pk
        super().save(*args, **kwargs)

        if criando and not self.codigo:
            self.codigo = gerar_codigo_movimentacao('saida', self.tipo, self.pk)
            super().save(update_fields=['codigo'])

        if criando:
            itens_decodados = json.loads(self.itens)
            for item in itens_decodados:
                produto_id = item.get('produto_id')
                quantidade = item.get('quantidade', 0)
                produto = Produto.objects.get(id=produto_id)
                atualizar_estoque(produto, quantidade, 'Saida')

class ItemSaida(models.Model):
    saida = models.ForeignKey('SaidaEstoque', on_delete=models.CASCADE, related_name='itens_saida', default="Sem Saida")
    produto = models.ForeignKey(Produto, on_delete=models.CASCADE, null=True, blank=True)
    quantidade = models.PositiveIntegerField(default=0)
    valor = MoneyField(max_digits=10, decimal_places=2, default_currency='BRL', null=True, blank=True)
    codigo = models.CharField(max_length=50, unique=True, editable=False, blank=True)

    def save(self, *args, **kwargs):
        criando = not self.pk
        super().save(*args, **kwargs)
        if criando and not self.codigo:
            self.codigo = f"{self.saida.codigo}-P{self.produto.pk:04}"
            super().save(update_fields=['codigo'])




# # class SaidaEstoque(models.Model):
# #     TIPOS_SAIDA = [
# #         ('venda',           'Venda'),
# #         ('ajuste',          'Ajuste'),
# #         ('perda',           'Perda'),
# #         ('transferencia',   'Transferência'),
# #         ('correcao',        'Correção'),
# #         ('outro',           'Outro'),
# #     ]

# #     codigo = models.CharField(max_length=20, unique=True, editable=False)
# #     tipo = models.CharField(max_length=20, choices=TIPOS_SAIDA)
# #     valor_total = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
# #     observacoes = models.TextField(blank=True, null=True)
# #     data_movimentacao = models.DateTimeField(default=timezone.now)
# #     usuario_responsavel = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

# #     def save(self, *args, **kwargs):
# #         if not self.pk:
# #             hoje = timezone.now().date()
# #             contador = EntradaEstoque.objects.filter(
# #                 tipo=self.tipo, data_movimentacao__date=hoje
# #             ).count() + 1
# #             self.codigo = gerar_codigo_movimentacao('saidas', self.tipo, numero_seq=contador)
# #         super().save(*args, **kwargs)

# #     def __str__(self):
# #         return f"{self.codigo} - {self.tipo}"

# # class ItemSaida(models.Model):
# #     movimentacao = models.ForeignKey(SaidaEstoque, on_delete=models.CASCADE, related_name='itens', null=True)
# #     produto = models.ForeignKey(Produto, on_delete=models.PROTECT)
# #     nome_produto = models.CharField(max_length=100, default='Sem nome')
# #     sku = models.CharField(max_length=50, default='Sem SKU')
# #     valor = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
# #     quantidade = models.PositiveIntegerField(default=0)
# #     usuario_responsavel = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
# #     data_movimentacao = models.DateTimeField(default=timezone.now)

# #     def save(self, *args, **kwargs):
# #         from .services import calcular_estoque_atual
# #         estoque = calcular_estoque_atual(self.produto.id)
# #         if self.quantidade > estoque:
# #             raise ValueError(f"Estoque insuficiente para o produto '{self.produto.nome}'. "
# #                              f"Disponível: {estoque}, solicitado: {self.quantidade}")
# #         super().save(*args, **kwargs)
