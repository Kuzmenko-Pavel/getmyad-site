# coding: utf-8
import sys

sys.path.append('.')

BROKER_URL = 'pyamqp://getmyad_site:123qwe@srv-4.yottos.com:5672/getmyad_site_celery'
BROKER_CONNECTION_MAX_RETRIES = 0
BROKER_HEARTBEAT = 0
CELERY_TASK_IGNORE_RESULT = True
CELERY_RESULT_BACKEND = "cache"
CELERY_CACHE_BACKEND = 'memcached://127.0.0.1:11211/'
CELERY_IMPORTS = ("getmyad.tasks.mail",)
CELERY_TASK_RESULT_EXPIRES = 7200
CELERY_ENABLE_UTC = False
CELERY_TIMEZONE = "Europe/Kiev"
CELERY_QUEUE_HA_POLICY = 'all'
CELERY_ACCEPT_CONTENT = ['pickle', 'json', 'application/text']
CELERYD_PREFETCH_MULTIPLIER = 1
