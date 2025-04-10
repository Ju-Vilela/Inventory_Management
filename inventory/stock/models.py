from django.db import models

class Produto(models.Model):
    item = models.CharField(max_length=100)
    categoria = models.CharField(max_length=100)
    marca = models.CharField(max_length=100)
    vendas = models.IntegerField(default=0)
    estoque = models.IntegerField()
    preco = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.item
