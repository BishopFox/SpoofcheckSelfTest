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
import argparse

from datetime import datetime
from libs.ConsoleColors import *

__version__ = 'v0.0.1'
current_time = lambda: str(datetime.now()).split(' ')[1].split('.')[0]


def serve():
    ''' Starts the application '''
    from handlers import start_server

    print(INFO + '%s : Starting application ...' % current_time())
    start_server()


def main(args):
    ''' Call functions in the correct order based on CLI params '''
    fpath = os.path.abspath(__file__)
    fdir = os.path.dirname(fpath)
    if fdir != os.getcwd():
        print(INFO + "Switching CWD to %s" % fdir)
        os.chdir(fdir)
    # Start server
    if args.start_server:
        serve()

# Main
if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Tornado WebApp',
    )
    parser.add_argument('-v', '--version',
                        action='version',
                        version=__version__,
                        )
    parser.add_argument("-s", "--start",
                        action='store_true',
                        dest='start_server',
                        help="start the server",
                        )
    main(parser.parse_args())
