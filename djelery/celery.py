# so celery.py module won't be misinterpreted with the library itself
from __future__ import absolute_import, unicode_literals

import os

from celery import Celery

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djelery.settings')

## app = Celery('tutorial', broker='pyamqp://guest@192.168.99.100//')
app = Celery('djelery')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django app configs.
# - app2/
#    - tasks.py => will be discovered
#    - models.py
# just like django finds moduls, this lets 
# celery find tasks.py in projects dirs
app.autodiscover_tasks()

# just an example, can be deleted, cuz real
# magic happens in tasks.py
@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))