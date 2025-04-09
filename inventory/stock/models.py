from django.db import models

class Produto(models.Model):
    item = models.CharField(max_length=200)
    categoria = models.CharField(max_length=100)
    status = models.CharField(max_length=20, choices=[('active', 'Active'), ('disabled', 'Disabled')])
    validade = models.DateField(null=True, blank=True)
    estoque = models.IntegerField(null=True, blank=True)
    preco = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.item
