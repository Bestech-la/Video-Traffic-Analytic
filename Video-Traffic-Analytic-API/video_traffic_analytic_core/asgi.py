
import os

from django.core.asgi import get_asgi_application

from channels.routing import ProtocolTypeRouter, URLRouter



os.environ.setdefault('DJANGO_SETTINGS_MODULE',
                      'video_traffic_analytic_core.settings_prod')

application = get_asgi_application()


application = ProtocolTypeRouter()

