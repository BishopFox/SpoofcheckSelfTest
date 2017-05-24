from celery import Celery
from tornado.options import options

from tasks.helpers import create_mq_url

queue_conf = {
    'CELERY_TASK_SERIALIZER': 'json',
    'CELERY_ACCEPT_CONTENT': ['json'],
    'CELERY_RESULT_SERIALIZER': 'json',
    'CELERY_TASK_RESULT_EXPIRES': 3600
}

selftest_task_queue = Celery(
    'selftest_task_queue',
    backend='rpc',
    broker=create_mq_url(options.mq_hostname, options.mq_port,
                         username=options.mq_username,
                         password=options.mq_password),
    include=[
        "tasks.message_tasks",
        "tasks.notifiers",
    ])
selftest_task_queue.conf.update(**queue_conf)