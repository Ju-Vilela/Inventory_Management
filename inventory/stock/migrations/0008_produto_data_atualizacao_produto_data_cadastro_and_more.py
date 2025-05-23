# Generated by Django 5.1.7 on 2025-05-09 23:03

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0007_alter_customuser_cargo_alter_produto_preco'),
    ]

    operations = [
        migrations.AddField(
            model_name='produto',
            name='data_atualizacao',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='produto',
            name='data_cadastro',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='produto',
            name='sku',
            field=models.CharField(blank=True, max_length=20, unique=True),
        ),
    ]
