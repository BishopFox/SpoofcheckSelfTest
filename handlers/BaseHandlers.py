# -*- coding: utf-8 -*-
'''
Created on Mar 15, 2012

@author: moloch

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

This file contains the base handlers, all other handlers should inherit
from these base classes.

'''


import traceback

from libs.ConfigManager import ConfigManager
from libs.SecurityDecorators import *
from tornado.web import RequestHandler
from tornado.ioloop import IOLoop
from tornado.websocket import WebSocketHandler


class BaseHandler(RequestHandler):
    ''' User handlers extend this class '''

    io_loop = IOLoop.instance()
    csp = {
        "default-src": ["'self'"],
        "script-src": [],
        "connect-src": [],
        "frame-src": [],
        "img-src": [],
        "media-src": [],
        "font-src": [],
        "object-src": [],
        "style-src": [],
    }

    def initialize(self):
        ''' Setup sessions, etc '''
        self.config = ConfigManager.instance()


    def set_default_headers(self):
        ''' Set security HTTP headers '''
        self.set_header("Server", "'; DROP TABLE server_types;--")
        self.add_header("X-Frame-Options", "DENY")
        self.add_header("X-XSS-Protection", "1; mode=block")
        self.add_header("X-Content-Type-Options", "nosniff")
        self._refresh_csp()

    def _refresh_csp(self):
        ''' Rebuild the Content-Security-Policy header '''
        _csp = ''
        for src, policies in self.csp.iteritems():
            if len(policies):
                _csp += "%s: %s;" % (src, " ".join(policies))
        self.set_header("Content-Security-Policy", _csp)

    def append_content_policy(self, src, policy):
        if src in self.csp:
            self.csp[src].append(policy)
            self._refresh_csp()
        else:
            raise ValueError("Invalid content source")

    def write_error(self, status_code, **kwargs):
        ''' Write our custom error pages '''
        if not self.config.debug:
            trace = "".join(traceback.format_exception(*kwargs["exc_info"]))
            logging.error("Request from %s resulted in an error code %d:\n%s" % (
                self.request.remote_ip, status_code, trace
            ))
            if status_code in [403]:
                # This should only get called when the _xsrf check fails,
                # all other '403' cases we just send a redirect to /403
                self.redirect('/403')
            else:
                # Never tell the user we got a 500
                self.render('public/404.html')
        else:
            # If debug mode is enabled, just call Tornado's write_error()
            super(BaseHandler, self).write_error(status_code, **kwargs)

    def get(self, *args, **kwargs):
        ''' Placeholder, incase child class does not impl this method '''
        self.render("public/404.html")

    def post(self, *args, **kwargs):
        ''' Placeholder, incase child class does not impl this method '''
        self.render("public/404.html")

    def put(self, *args, **kwargs):
        ''' Log odd behavior, this should never get legitimately called '''
        logging.warn(
            "%s attempted to use PUT method" % self.request.remote_ip
        )

    def delete(self, *args, **kwargs):
        ''' Log odd behavior, this should never get legitimately called '''
        logging.warn(
            "%s attempted to use DELETE method" % self.request.remote_ip
        )

    def head(self, *args, **kwargs):
        ''' Ignore it '''
        logging.warn(
            "%s attempted to use HEAD method" % self.request.remote_ip
        )

    def options(self, *args, **kwargs):
        ''' Log odd behavior, this should never get legitimately called '''
        logging.warn(
            "%s attempted to use OPTIONS method" % self.request.remote_ip
        )

    def on_finish(self, *args, **kwargs):
        ''' Called after a response is sent to the client '''
        pass


class BaseWebSocketHandler(WebSocketHandler):
    ''' Handles websocket connections '''

    def initialize(self):
        ''' Setup sessions, etc '''
        self.config = ConfigManager.instance()

    def open(self):
        pass

    def on_message(self, message):
        pass

    def on_close(self):
        pass