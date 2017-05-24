# -*- coding: utf-8 -*-
"""
@author: moloch
Copyright 2016
"""
import json
import logging

from celery.utils.log import get_task_logger

from libs.events import TASK_EVENTS, TASK_ROUTING_KEY
from tasks import selftest_task_queue
from tasks.helpers.mq import mq_send_once


LOGGER = get_task_logger(__name__)


@selftest_task_queue.task
def task_complete_notify(result, task_id):
    """ Notifies consumers that a task has been completed """
    logging.debug('Task result is: %r', result)
    logging.critical('Sending complete notification for id: %s', task_id)
    msg = json.dumps({'task_id': task_id})
    if mq_send_once(TASK_EVENTS, TASK_ROUTING_KEY, msg):
        logging.info('Confirmed delivery of task complete notification')
    else:
        logging.warning('Could not confirm task complete notification delivery')
