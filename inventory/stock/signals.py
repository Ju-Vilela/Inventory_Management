from django.contrib.auth.models import Group, Permission
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

def aplicar_permissoes_post_migrate(sender, **kwargs):
    print("Aplicando permissões após migração...")

    permissoes_por_cargo = {
        'admin': [
            "acesso_total",
            "gestao_produtos",
            "gestao_usuarios",
            "config_usuarios",
            "cadastrar_produtos",
            "editar_produtos",
            "entrada",
            "saida",
            "alterar_status",
            "ver_historico",
            "receber_alertas",
        ],
        'gerente': [
            "gestao_produtos",
            "cadastrar_produtos",
            "editar_produtos",
            "entrada",
            "saida",
            "alterar_status",
            "ver_historico",
            "receber_alertas",
        ],
        'vendedor': [
            "editar_produtos",
            "saida",
            "alterar_status",
            "ver_historico",
            "receber_alertas",
        ],
    }
    class Permissoes:
        ACESSO_TOTAL = 'Acesso Total'
        GESTAO_PRODUTOS = 'Gestão de Produtos'
        GESTAO_USUARIOS = 'Gestão de Usuários'
        CONFIG_USUARIOS = 'Configurações de Usuários'
        CADASTRAR = 'Cadastrar produtos'
        EDITAR = 'Editar produtos'
        ENTRADA = 'Entrada de estoque'
        SAIDA = 'Saída de produtos'
        ALTERAR_STATUS = 'Alterar status (ativo/inativo)'
        HISTORICO = 'Ver histórico'
        ALERTAS = 'Receber alertas'

    mapa_codename = {
        Permissoes.ACESSO_TOTAL: "acesso_total",
        Permissoes.GESTAO_PRODUTOS: "gestao_produtos",
        Permissoes.GESTAO_USUARIOS: "gestao_usuarios",
        Permissoes.CONFIG_USUARIOS: "config_usuarios",
        Permissoes.CADASTRAR: "cadastrar_produtos",
        Permissoes.EDITAR: "editar_produtos",
        Permissoes.ENTRADA: "entrada",
        Permissoes.SAIDA: "saida",
        Permissoes.ALTERAR_STATUS: "alterar_status",
        Permissoes.HISTORICO: "ver_historico",
        Permissoes.ALERTAS: "receber_alertas",
    }

    for cargo, permissoes in permissoes_por_cargo.items():
        grupo, _ = Group.objects.get_or_create(name=cargo)
        grupo.permissions.clear()

        for codename in permissoes:
            try:
                perm = Permission.objects.get(codename=codename)
                grupo.permissions.add(perm)
                print(f"[√] Permissão '{codename}' adicionada ao grupo '{cargo}'")
            except Permission.DoesNotExist:
                print(f"[!] Permissão '{codename}' não encontrada para o grupo '{cargo}'")

User = get_user_model()

@receiver(post_save, sender=User)
def atribuir_grupo_usuario(sender, instance, created, **kwargs):
    if instance.cargo:
        grupo = Group.objects.filter(name=instance.cargo).first()
        if grupo:
            instance.groups.clear()  # remove grupos antigos
            instance.groups.add(grupo)
            print(f"[★] Usuário '{instance.username}' associado ao grupo '{grupo.name}'")