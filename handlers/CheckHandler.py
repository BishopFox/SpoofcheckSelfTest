from handlers.BaseHandlers import BaseWebSocketHandler
import logging
import json


class MonitorSocketHandler(BaseWebSocketHandler):

    def open(self):
        logging.debug("[WebSocket] Opened a Monitor Websocket")
        self._setup_opcodes()

    def _setup_opcodes(self):
        self.opcodes = {
            "check": self.check_domain
        }

    def on_message(self, message):
        ''' Routes response to the correct opcode '''
        try:
            message = json.loads(message)
            if 'opcode' in message and message['opcode'] in self.opcodes:
                self.opcodes[message['opcode']](message)
            else:
                raise Exception("Malformed message")
        except Exception as error:
            self.send_error('Error', str(error))
            logging.exception(
                '[WebSocket]: Exception while routing json message')

    # Opcodes
    def check_domain(self, message):

        # TODO: Add real DNS checking here

        import time
        time.sleep(2)
        # self.write_message({
        #     'opcode': "test",
        #     'message': "asdfasdfasdfasdfasdfasdf"
        # })
