import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
app = Celery('core')
app.config_from_object('django.conf:settings', namespace='CELERY')
# Update the configuration to include the new setting
app.conf.update(
    broker_connection_retry_on_startup=True,
)
app.autodiscover_tasks()