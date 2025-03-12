"""
Configuration for the core application of the Metamorph project.

This module defines the AppConfig for the 'core' app and sets up any necessary
startup tasks (such as triggering an immediate data fetch via Celery).
"""

from django.apps import AppConfig

class CoreConfig(AppConfig):
    """
    App configuration for the core application.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        from core.tasks import fetch_all_data
        fetch_all_data.delay()
