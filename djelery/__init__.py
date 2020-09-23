from __future__ import absolute_import, unicode_literals

# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
from .celery import app as celery_app

# this is a celery entrypoint, so it will got for dj_celery, 
# find here __init__ and run app from celery.py module
__all__ = ('celery_app',)