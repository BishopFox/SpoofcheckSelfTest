from handlers.BaseHandlers import BaseWebSocketHandler
import logging
import json
import re

from tornado.gen import coroutine

from mixins.celery_task_mixin import CeleryTaskMixin

from tasks.message_tasks import *


class MonitorSocketHandler(BaseWebSocketHandler, CeleryTaskMixin):

    def open(self):
        logging.debug("[WebSocket] Opened a Monitor Websocket")
        self._setup_opcodes()

    def _setup_opcodes(self):
        self.opcodes = {
            "check": self.check_domain
        }

    @coroutine
    def on_message(self, message):
        ''' Routes response to the correct opcode '''
        try:
            message = json.loads(message)
            if 'opcode' in message and message['opcode'] in self.opcodes:
                yield self.opcodes[message['opcode']](message)
            else:
                raise Exception("Malformed message")
        except Exception as error:
            self.send_error('Error', str(error))
            logging.exception(
                '[WebSocket]: Exception while routing json message')


    # Opcodes
    @coroutine
    def check_domain(self, message):
        try:
            domain = message["domain"]

            groups = re.search("@([\w.]+)", domain)

            if groups is not None:
                domain = groups.group(1)

            recaptcha_solution = message["captchaResponse"]

            ip_address = self.request.remote_ip

            solution_correct = yield self.execute_task(check_recaptcha_solution, **{
                "user_solution": recaptcha_solution,
                "ip_address": ip_address
            })

            logging.debug(solution_correct)

            if not solution_correct:
                output = {
                    "opcode": "fail",
                    "reason": "Failed Recaptcha"
                }

                self.write_message(output)

            else:
                logging.info("Checking domain " + domain)
                output = yield self.execute_task(email_spoofing_analysis, **{
                    "domain": domain
                })

                self.write_message(output)
        except Exception as error:
                logging.exception(error)
