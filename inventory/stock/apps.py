from django.apps import AppConfig
from django.db.models.signals import post_migrate

class CoreConfig(AppConfig):
    name = 'stock'

    def ready(self):
        from .signals import aplicar_permissoes_post_migrate
        post_migrate.connect(aplicar_permissoes_post_migrate, sender=self)