# -*- coding: utf-8 -*-
'''
@author: moloch

    Copyright 2012

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


import os
import sys
import urllib
import socket
import getpass
import logging
import ConfigParser

from libs.ConsoleColors import *
from libs.Singleton import Singleton


logging_levels = {
       'notset': logging.NOTSET,
        'debug': logging.DEBUG,
         'info': logging.INFO,
  'information': logging.INFO,
         'warn': logging.WARN,
      'warning': logging.WARN,
}


@Singleton
class ConfigManager(object):
    ''' Central class which handles any user-controlled settings '''

    def __init__(self, cfg_file='app.cfg'):
        self.filename = cfg_file
        if os.path.exists(cfg_file) and os.path.isfile(cfg_file):
            self.conf = os.path.abspath(cfg_file)
        else:
            sys.stderr.write(WARN+"No configuration file found at: %s." % self.conf)
            os._exit(1)
        self.refresh()
        self.__logging__()

    def __logging__(self):
        ''' Load network configurations '''
        level = self.config.get("Logging", 'console_level').lower()
        logger = logging.getLogger()
        logger.setLevel(logging_levels.get(level, logging.NOTSET))
        if self.config.getboolean("Logging", 'file_logs'):
            self._file_logger(logger)

    def _file_logger(self, logger):
        ''' Configure File Logger '''
        file_handler = logging.FileHandler('%s' % self.logfilename)
        logger.addHandler(file_handler)
        file_format = logging.Formatter('[%(levelname)s] %(asctime)s - %(message)s')
        file_handler.setFormatter(file_format)
        flevel = self.config.get("Logging", 'file_logs_level').lower()
        file_handler.setLevel(logging_levels.get(flevel, logging.NOTSET))

    def refresh(self):
        ''' Refresh config file settings '''
        self.config = ConfigParser.SafeConfigParser()
        self.config_fp = open(self.conf, 'r')
        self.config.readfp(self.config_fp)

    def save(self):
        ''' Write current config to file '''
        self.config_fp.close()
        fp = open(self.conf, 'w')
        self.config.write(fp)
        fp.close()
        self.refresh()

    @property
    def logfilename(self):
        return self.config.get("Logging", 'file_logs_filename')

    @property
    def listen_port(self):
        ''' Web app listen port, only read once '''
        lport = self.config.getint("Server", 'port')
        if not 0 < lport < 65535:
            logging.fatal("Listen port not in valid range: %d" % lport)
            os._exit(1)
        return lport

    @property
    def bootstrap(self):
        return self.config.get("Server", 'bootstrap')

    @property
    def log_filename(self):
        return self.config.get("Logging", 'log_filename')

    @property
    def debug(self):
        ''' Debug mode '''
        return self.config.getboolean("Server", 'debug')

    @debug.setter
    def debug(self, value):
        assert isinstance(value, bool)
        self.config.set("Server", 'debug', str(value))

    @property
    def domain(self):
        ''' Automatically resolve domain, or use manual setting '''
        _domain = self.config.get("Server", 'domain').strip()
        if _domain.lower() == 'auto':
            try:
                _domain = socket.gethostbyname(socket.gethostname())
                # On some Linux systems the hostname resolves to ~127.0.0.1
                # per /etc/hosts, so fallback and try to get the fqdn if we can.
                if _domain.startswith('127.'):
                    _domain = socket.gethostbyname(socket.getfqdn())
            except:
                logging.warn("Failed to automatically resolve domain, please set manually")
                _domain = 'localhost'
            logging.debug("Domain was automatically configured to '%s'" % _domain)
        if _domain == 'localhost' or _domain.startswith('127.') or _domain == '::1':
            logging.warn("Possible misconfiguration 'domain' is set to 'localhost'")
        return _domain

    @property
    def origin(self):
        http = 'https://' if self.use_ssl else 'http://'
        return "%s%s:%d" % (http, self.domain, self.listen_port)

    @property
    def memcached(self):
        ''' Memached settings, cannot be changed from webui '''
        host = self.config.get("Memcached", 'host')
        port = self.config.getint("Memcached", 'port')
        if not 0 < port < 65535:
            logging.fatal("Memcached port not in valid range: %d" % port)
            os._exit(1)
        return "%s:%d" % (host, port)

    @property
    def session_duration(self):
        ''' Max session age in seconds '''
        return abs(self.config.getint("Sessions", 'max_age'))

    @property
    def admin_ips(self):
        ''' Whitelist admin ip address, this may be bypassed if x-headers is enabled '''
        ips = self.config.get("Security", 'admin_ips')
        ips = ips.replace(" ", "").split(',')
        ips.append('127.0.0.1')
        ips.append('::1')
        return tuple(set(ips))

    @property
    def x_headers(self):
        ''' Enable/disable HTTP X-Headers '''
        xheaders = self.config.getboolean("Security", 'x-headers')
        if xheaders:
            logging.warn("X-Headers is enabled, this may affect IP security restrictions")
        return xheaders

    @property
    def use_ssl(self):
        ''' Enable/disabled SSL server '''
        return self.config.getboolean("Ssl", 'use_ssl')

    @property
    def certfile(self):
        ''' SSL Certificate file path '''
        cert = os.path.abspath(self.config.get("Ssl", 'certificate_file'))
        if not os.path.exists(cert):
            logging.fatal("SSL misconfiguration, certificate file '%s' not found." % cert)
            os._exit(1)
        return cert

    @property
    def keyfile(self):
        ''' SSL Key file path '''
        key = os.path.abspath(self.config.get("Ssl", 'key_file'))
        if not os.path.exists(key):
            logging.fatal("SSL misconfiguration, key file '%s' not found." % key)
            os._exit(1)
        return key

    @property
    def db_connection(self):
        ''' Construct the database connection string '''
        dialect = self.config.get("Database", 'dialect').lower().strip()
        dialects = {
            'sqlite': self._sqlite,
            'postgresql': self._postgresql,
            'mysql': self._mysql,
        }
        _db = dialects.get(dialect, self._sqlite)()
        self._test_connection(_db)
        return _db

    def _postgresql(self):
        '''
        Configure to use postgresql, there is not built-in support for postgresql
        so make sure we can import the 3rd party python lib 'pypostgresql'
        '''
        logging.debug("Configured to use Postgresql for a database")
        try:
            import pypostgresql
        except ImportError:
            print(WARN+"You must install 'pypostgresql' to use a postgresql database.")
            os._exit(1)
        db_host, db_name, db_user, db_password = self._db_credentials()
        return 'postgresql+pypostgresql://%s:%s@%s/%s' % (
            db_user, db_password, db_host, db_name,
        )

    def _sqlite(self):
        ''' SQLite connection string, always save db file to cwd, or in-memory '''
        logging.debug("Configured to use SQLite for a database")
        db_name = os.path.basename(self.config.get("Database", 'name'))
        if not len(db_name):
            db_name = 'app'
        return ('sqlite:///%s.db' % db_name) if db_name != ':memory:' else 'sqlite://'

    def _mysql(self):
        ''' Configure db_connection for MySQL '''
        logging.debug("Configured to use MySQL for a database")
        db_server, db_name, db_user, db_password = self._db_credentials()
        return 'mysql://%s:%s@%s/%s' % (
            db_user, db_password, db_server, db_name
        )

    def _test_connection(self, connection_string):
        ''' Test the connection string to see if we can connect to the database'''
        engine = create_engine(connection_string)
        try:
            connection = engine.connect()
            connection.close()
        except:
            if self.debug:
                logging.exception("Database connection failed")
            logging.critical("Failed to connect to database, check .cfg")
            os._exit(1)

    def _db_credentials(self):
        ''' Pull db creds and return them url encoded '''
        host = self.config.get("Database", 'host')
        name = self.config.get("Database", 'name')
        user = self.config.get("Database", 'user')
        password = self.config.get("Database", 'password')
        if user == '' or user == 'RUNTIME':
            user = raw_input(PROMPT+"Database User: ")
        if password == '' or password == 'RUNTIME':
            sys.stdout.write(PROMPT+"Database password: ")
            sys.stdout.flush()
            password = getpass.getpass()
        db_host = urllib.quote(host)
        db_name = urllib.quote(name)
        db_user = urllib.quote(user)
        db_password = urllib.quote_plus(password)
        return db_host, db_name, db_user, db_password

