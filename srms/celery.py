from __future__ import absolute_import

import os

from celery import Celery

# from __future__ import absolute_import
# set the default Django settings module for the 'celery' program.
from celery.schedules import crontab

# app.conf.beat_schedule = {
#     # Executes every Monday morning at 7:30 a.m.
#     'add-every-monday-morning': {
#         'task': 'tasks.add',
#         'schedule': crontab(hour=7, minute=30, day_of_week=1),
#         'args': (16, 16),
#     },
# }

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'srms.settings')

app = Celery('srms')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

app.conf.beat_schedule={
    # 'quiz-auto-submit':{
    #     'task':'ubfquiz.tasks.auto_submit_task',
    #     'schedule':60,
    # },
     'every-1-minute':{
         'task':'student.tasks.Student_absent',
         'schedule':60,
     },
    # 'everyday-sub-checker':{
    #     'task':'student.tasks.subscription_checker',
    #     'schedule':60,
    # },
     'everyday-Notification-due':{
         'task':'core.tasks.Notification_centre',
         'schedule':60,
     },
    # 'usage-alert':{
    #     'task':'student.tasks.Usage',
    #     'schedule':60,        
    # },
    # 'promocode-check':{
    #     'task':'ubfcart.tasks.promocodechecker',
    #     'schedule':60,
    # },
    'owner-sub':{
        'task':'owner.tasks.owner_subscription_checker',
        'schedule':60,
    },
    'quiz-rollout':{
        'task':'ubfquiz.tasks.quiz_rollout',
        'schedule':60,
    }
}
# Load task modules from all registered Django app configs.
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
