import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "inventory.settings")

application = get_wsgi_application()

# Adiciona um alias para o Vercel reconhecer
app = application