# -*- coding: utf-8 -*-
"""
@author: moloch
Copyright 2016
"""

import pika

from tornado.options import options
from furl import furl


def create_mq_url(hostname, port, username=None, password=None):
    """ Creates a well formed amqp:// connection URI """
    mq_url = furl()
    mq_url.scheme = "amqp"
    mq_url.host = hostname
    mq_url.port = port
    mq_url.username = username
    mq_url.password = password
    return str(mq_url)


def mq_connect():
    """ Connects to the MQ and returns the connection """
    _url = create_mq_url(options.mq_hostname, options.mq_port,
                         username=options.mq_username,
                         password=options.mq_password)
    parameters = pika.URLParameters(_url)
    connection = pika.BlockingConnection(parameters)
    return connection


def mq_send(channel, exchange, routing_key, message):
    """
    Sends an MQ message on a channel to an exchange returns confirmation
    """
    return channel.basic_publish(exchange, routing_key, message,
                                 pika.BasicProperties(content_type='text/plain',
                                                      delivery_mode=1))


def mq_send_once(exchange, routing_key, message):
    """
    Publishes a single rabbit mq message, and returns the
    delivery confirmation.

    NOTE: If you're wondering the reason for using this over
    `libs.events.event_producers` those producers are dependent
    on the Tornado ioloop, which we don't have here, nor do we
    want here.
    """
    connection = mq_connect()
    confirmation = mq_send(connection.channel(), exchange, routing_key, message)
    connection.close()
    return confirmation
