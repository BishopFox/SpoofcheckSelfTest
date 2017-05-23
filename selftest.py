#!/usr/bin/env python
'''
    Copyright 2012 Root the Box

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
----------------------------------------------------------------------------

This file is the main starting point for the application, based on the
command line arguments it calls various components setup/start/etc.

'''

import os
import sys

from tornado.options import options, define

from datetime import datetime
from libs.ConsoleColors import *

__version__ = 'v0.0.1'
current_time = lambda: str(datetime.now()).split(' ')[1].split('.')[0]


def serve():
    ''' Starts the application '''
    from handlers import start_server

    print(INFO + '%s : Starting application ...' % current_time())
    start_server()


def start_worker():
    from tasks import selftest_task_queue
    from tasks.helpers import create_mq_url
    from celery.bin import worker

    worker = worker.worker(app=selftest_task_queue)
    worker_options = {
        'broker': create_mq_url(options.mq_hostname, options.mq_port,
                                username=options.mq_username,
                                password=options.mq_password),
        'loglevel': options.mq_loglevel,
        'traceback': options.debug,
    }
    worker.run(**worker_options)


def main():
    ''' Call functions in the correct order based on CLI params '''
    fpath = os.path.abspath(__file__)
    fdir = os.path.dirname(fpath)
    if fdir != os.getcwd():
        print(INFO + "Switching CWD to %s" % fdir)
        os.chdir(fdir)
    if options.api:
        serve()
    elif options.celery:
        start_worker()
    else:
        print(INFO + "Failed to start server")

define("config",
       default="app.cfg",
       help="path to config file",
       type=str,
       callback=lambda path: options.parse_config_file(path, final=False))

# RabbitMQ host
define("mq_hostname",
       group="mq",
       default=os.environ.get("SPOOFCHECK_MQ_HOST", "127.0.0.1"),
       help="the mq host")

define("mq_port",
       group="mq",
       default="5672",
       help="the mq port",
       type=str)

define("mq_username",
       group="mq",
       default=os.environ.get("SPOOFCHECK_MQ_USERNAME", "guest"),
       help="the mq username",
       type=str)

define("mq_password",
       group="mq",
       default=os.environ.get("SPOOFCHECK_MQ_PASSWORD", "guest"),
       help="the mq password",
       type=str)

define("mq_loglevel",
       group="mq",
       default=os.environ.get("SPOOFCHECK_MQ_LOGLEVEL", "INFO"),
       help="the mq log level")

define("debug",
       default=bool(os.environ.get("SPOOFCHECK_DEBUG", False)),
       help="start server in debugging mode",
       group="debug",
       type=bool)

define("celery",
       default=False,
       help="Start Celery task server",
       type=bool)

define("api",
       default=False,
       help="Start Server",
       type=bool)


# Main
if __name__ == '__main__':
    try:
        options.parse_command_line()
    except IOError as error:
        print(WARN + str(error))
        sys.exit()
    main()

