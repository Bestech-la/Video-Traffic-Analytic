import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE',
                      'video_traffic_analytic_core.settings_prod')

application = get_wsgi_application()

