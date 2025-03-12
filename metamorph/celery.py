"""
Celery configuration for the Metamorph project.

This module configures Celery to work with Django and loads task modules from all 
registered Django apps. It also sets a periodic task schedule for fetching data.
"""

import os
from celery import Celery

# Set the default Django settings module for the Celery program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'metamorph.settings')

app = Celery('metamorph')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Optional: additional periodic tasks can be defined here.
app.conf.beat_schedule = {
    'fetch-data-every-5-minutes': {
        'task': 'core.tasks.fetch_all_data',
        'schedule': 300.0,  # every 5 minutes
    },
}
