# -*- coding: utf-8 -*-
'''
@author: moloch

    Copyright 2013

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
'''

import logging

from os import urandom
from tornado import netutil
from tornado.web import Application, StaticFileHandler
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from libs.ConfigManager import ConfigManager
from handlers.ErrorHandlers import *
from handlers.HomePageHandler import *
from handlers.CheckHandler import *

from libs.events.event_consumers import TaskEventConsumer

# Config
config = ConfigManager.instance()


def start_server():
    ''' Main entry point for the application '''

    task_event_consumer = TaskEventConsumer()

    # Application setup
    app = Application([

        # Static Handlers - Serves static CSS, JS and images
        (r'/static/(.*\.(css|js|png|jpg|jpeg|svg|ttf|html|json))',
         StaticFileHandler, {'path': 'static/'}),

        # Home page serving SPA app
        (r'/', HomePageHandler),

        # Monitor Socket
        (r'/connect/monitor', MonitorSocketHandler),

        # Error Handlers -
        (r'/403', ForbiddenHandler),

        # Catch all 404 page
        (r'(.*)', NotFoundHandler),
    ],

        # Randomly generated secret key
        cookie_secret=urandom(32).encode('hex'),

        # Request that does not pass @authorized will be
        # redirected here
        forbidden_url='/403',

        # Requests that does not pass @authenticated  will be
        # redirected here
        login_url='/login',

        # Template directory
        template_path='templates/',

        # Debug mode
        debug=config.debug,

        task_event_consumer=task_event_consumer
    )

    sockets = netutil.bind_sockets(config.listen_port)
    if config.use_ssl:
        server = HTTPServer(app,
                            ssl_options={
                                "certfile": config.certfile,
                                "keyfile": config.keyfile,
                            },
                            xheaders=config.x_headers)
    else:
        server = HTTPServer(app, xheaders=config.x_headers)
    server.add_sockets(sockets)
    io_loop = IOLoop.instance()
    try:
        io_loop.add_callback(task_event_consumer.connect)
        io_loop.start()
    except KeyboardInterrupt:
        logging.warn("Keyboard interrupt, shutdown everything!")
    except:
        logging.exception("Main I/O Loop threw an excetion!")
    finally:
        io_loop.stop()
