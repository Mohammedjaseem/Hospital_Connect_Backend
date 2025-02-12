from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Hospital_Connect.settings')

app = Celery('Hospital_Connect')

# Use a string here to avoid importing the Django settings file directly.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Discover tasks in installed apps automatically.
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")