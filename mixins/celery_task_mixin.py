# -*- coding: utf-8 -*-
"""
@author: moloch
Copyright 2016
"""

import logging

from uuid import uuid4

from tornado.gen import coroutine, Return, Task

from tasks.notifiers import task_complete_notify


class CeleryTaskMixin(object):

    @property
    def task_event_consumer(self):
        return self.settings["task_event_consumer"]

    @coroutine
    def execute_task(self, task, *args, **kwargs):
        """ Allows tasks to be executed using coroutines """
        result = yield Task(self._execute_task, task, *args, **kwargs)
        raise Return(result.result)

    def _execute_task(self, task, *args, **kwargs):
        """ Not thread safe, only call this once per-notification """
        logging.critical('task = %r', task)
        logging.critical('args = %r', args)
        logging.critical('kwargs = %r', kwargs)

        self._callback = kwargs['callback']
        del kwargs['callback']

        task_id = str(uuid4())
        self.task_event_consumer.add_event_listener(self, task_id)
        self._task_result = task.apply_async(args, kwargs,
                                             task_id=task_id,
                                             link=task_complete_notify.s(task_id))

    def on_task_completed(self):
        self._callback(self._task_result)
