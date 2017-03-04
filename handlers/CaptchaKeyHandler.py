import json

from handlers.BaseHandlers import BaseHandler


class CaptchaKeyHandler(BaseHandler):

    def get(self, *args, **kwargs):
        output = {
            "status": "OK",
            # TODO: Replace with values taken from env variables
            "publicKey": "6LdIoBcUAAAAAPCPungbnm_WHG3tmukpaLpGuVra",
        }
        self.write(output)
