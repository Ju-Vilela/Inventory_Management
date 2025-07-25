# Generated by Django 5.1.7 on 2025-05-23 23:04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0025_alter_customuser_cargo'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='customuser',
            options={'permissions': [('gestao_produtos', 'Pode gerenciar produtos'), ('gestao_usuarios', 'Pode gerenciar usuários'), ('config_usuarios', 'Pode configurar usuários'), ('cadastrar_produtos', 'Pode cadastrar produtos'), ('editar_produtos', 'Pode editar produtos'), ('atualizar_estoque', 'Pode atualizar estoque'), ('registrar_vendas', 'Pode registrar vendas'), ('alterar_status', 'Pode alterar status de produtos'), ('ver_historico', 'Pode ver histórico'), ('receber_alertas', 'Pode receber alertas')]},
        ),
    ]
