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
import functools


def csp(src, policy):
    ''' Decorator for easy CSP management '''

    def func(method):
        @functools.wraps(method)
        def wrapper(self, *args, **kwargs):
            self.add_content_policy(src, policy)
        return wrapper
    return func



def restrict_ip_address(method):
    ''' Only allows access to ip addresses in a provided list '''

    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if self.request.remote_ip in self.application.settings['admin_ips']:
            return method(self, *args, **kwargs)
        else:
            self.redirect(self.application.settings['forbidden_url'])
    return wrapper


def restrict_origin(method):
    ''' Check the origin header / prevent CSRF+WebSocket '''

    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if self.request.headers['Origin'] == self.config.origin:
            return method(self, *args, **kwargs)
    return wrapper