"""
WSGI config for shido project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

from shido.info import log_settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shido.settings')

application = get_wsgi_application()

log_settings()