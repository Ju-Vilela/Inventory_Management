import os
import sys
from django.core.wsgi import get_wsgi_application

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'inventory'))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "inventory.settings")

application = get_wsgi_application()

# Adiciona um alias para o Vercel reconhecer
app = application