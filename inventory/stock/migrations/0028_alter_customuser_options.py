# Generated by Django 5.1.7 on 2025-05-24 01:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stock', '0027_alter_customuser_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='customuser',
            options={'permissions': [('acesso_total', 'Acesso Total'), ('gestao_produtos', 'Gestão de Produtos'), ('gestao_usuarios', 'Gestão de Usuários'), ('config_usuarios', 'Configurações de Usuários'), ('cadastrar_produtos', 'Cadastrar produtos'), ('editar_produtos', 'Editar produtos'), ('entrada', 'Entrada de estoque'), ('saida', 'Saída de Produtos'), ('alterar_status', 'Alterar status (ativo/inativo)'), ('ver_historico', 'Ver histórico'), ('receber_alertas', 'Receber alertas')]},
        ),
    ]
