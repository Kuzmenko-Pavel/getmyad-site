# coding: utf-8
import sys

sys.path.append('.')

BROKER_URL = 'pyamqp://getmyad_site:123qwe@srv-4.yottos.com:5672/getmyad_site_celery'
BROKER_CONNECTION_MAX_RETRIES = 0
BROKER_HEARTBEAT = 0
CELERY_TASK_IGNORE_RESULT = True
CELERY_IMPORTS = ("getmyad.tasks.mail", "getmyad.tasks.adload")
CELERY_TASK_RESULT_EXPIRES = 1
CELERY_RESULT_PERSISTENT = False
CELERY_ENABLE_UTC = False
CELERY_TIMEZONE = "Europe/Kiev"
CELERY_QUEUE_HA_POLICY = 'all'
CELERY_ACCEPT_CONTENT = ['pickle', 'json', 'application/text']
CELERYD_PREFETCH_MULTIPLIER = 1
