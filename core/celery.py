import os
import environ
from celery import Celery


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
env = environ.Env()


# Check if Celery is enabled
if env.bool('CELERY_ENABLED', default=False):
    app = Celery('core')
    app.config_from_object('django.conf:settings', namespace='CELERY')
    app.conf.update(
        broker_connection_retry_on_startup=True,
    )
    app.autodiscover_tasks()