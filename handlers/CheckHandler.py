from handlers.BaseHandlers import BaseWebSocketHandler
import logging
import json
import os
import requests

import emailprotectionslib.spf as spflib
import emailprotectionslib.dmarc as dmarclib


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

    def check_recaptcha_solution(self, user_solution):
        payload = {
            "secret": os.environ["RECAPTCHA_SECRET_KEY"],
            "response": user_solution,
            "remoteip": self.request.remote_ip,
        }

        recaptcha_response = requests.post("https://www.google.com/recaptcha/api/siteverify", data=payload)

        logging.info("[RECAPTCHA Response] " + recaptcha_response.text)

        return recaptcha_response.json()["success"]


    # Opcodes
    def check_domain(self, message):
        domain = message["domain"]

        recaptcha_solution = message["captchaResponse"]

        solution_correct = self.check_recaptcha_solution(recaptcha_solution)

        if not solution_correct:
            output = {
                "opcode": "fail",
                "reason": "Failed Recaptcha"
            }

            self.write(output)

        else:

            spf_record = spflib.SpfRecord.from_domain(domain)
            dmarc_record = dmarclib.DmarcRecord.from_domain(domain)

            spf_existence = spf_record.record is not None
            spf_strong = spf_record.is_record_strong() if spf_existence else False

            dmarc_existence = dmarc_record.record is not None
            dmarc_policy = ""
            dmarc_strong = False
            dmarc_aggregate_reports = False
            dmarc_forensic_reports = False

            org_domain = None
            org_record_record = None
            org_sp = None
            org_policy = None
            org_aggregate_reports = None
            org_forensic_reports = None

            is_subdomain = False

            if dmarc_record is not None:
                dmarc_strong = dmarc_record.is_record_strong()
                dmarc_policy = dmarc_record.policy
                dmarc_aggregate_reports = dmarc_record.rua is not None and dmarc_record.rua != ""
                dmarc_forensic_reports = dmarc_record.ruf is not None and dmarc_record.ruf != ""

            if not dmarc_existence:
                try:
                    org_domain = dmarc_record.get_org_domain()
                    org_record = dmarc_record.get_org_record()
                    org_record_record = org_record.record
                    org_sp = org_record.subdomain_policy
                    org_policy = org_record.policy
                    org_aggregate_reports = dmarc_record.rua is not None and org_record.rua != ""
                    org_forensic_reports = dmarc_record.ruf is not None and org_record.ruf != ""
                    is_subdomain = True
                except dmarclib.OrgDomainException:
                    org_domain = None
                    org_record_record = None
                    org_sp = None
                    org_policy = None
                    org_aggregate_reports = None
                    org_forensic_reports = None

            domain_vulnerable = not (dmarc_strong and (spf_strong or org_domain is not None))

            output = {
                'opcode': "test",
                'message': {
                    'vulnerable': domain_vulnerable,
                    'isSubdomain': is_subdomain,
                    'spf': {
                        'existence': spf_existence,
                        'strongConfiguration': spf_strong,
                        'record': spf_record.record if spf_existence else None,
                    },
                    'dmarc': {
                        'existence': dmarc_existence,
                        'policy': dmarc_policy,
                        'aggregateReports': dmarc_aggregate_reports,
                        'forensicReports': dmarc_forensic_reports,
                        'record': dmarc_record.record if dmarc_existence else None,
                        'orgRecord': {
                            'existence': org_record_record is not None,
                            'domain': org_domain,
                            'record': org_record_record,
                            'sp': org_sp,
                            'policy': org_policy,
                            'rua': org_aggregate_reports,
                            'ruf': org_forensic_reports,
                        },
                    },

                },
            }

            self.write_message(output)
