import os

from django.core.wsgi import get_wsgi_application
from inventory.wsgi import application

# O Vercel precisa de um "handler" para rodar a aplicação
app = application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'inventory.settings')

application = get_wsgi_application()
