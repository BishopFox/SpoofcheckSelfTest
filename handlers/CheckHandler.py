from handlers.BaseHandlers import BaseWebSocketHandler
import logging
import json

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

    # Opcodes
    def check_domain(self, message):

        domain = message["domain"]

        spf_record = spflib.SpfRecord.from_domain(domain)
        dmarc_record = dmarclib.DmarcRecord.from_domain(domain)

        spf_existence = spf_record.record is not None
        spf_strong = spf_record.is_record_strong() if spf_existence else False

        dmarc_existence = dmarc_record.record is not None
        dmarc_policy = ""
        dmarc_strong = False
        dmarc_aggregate_reports = False
        dmarc_forensic_reports = False

        org_domain = ""
        org_record_record = ""
        org_sp = ""
        org_policy = ""

        if dmarc_record is not None:
            dmarc_strong = dmarc_record.is_record_strong()
            dmarc_policy = dmarc_record.policy
            dmarc_aggregate_reports = dmarc_record.rua is not None and dmarc_record.rua != ""
            dmarc_forensic_reports = dmarc_record.ruf is not None and dmarc_record.ruf != ""

        if not dmarc_existence:
            org_domain = dmarc_record.get_org_domain()
            org_record = dmarc_record.get_org_record()
            org_record_record = org_record.record
            org_sp = org_record.subdomain_policy
            org_policy = org_record.policy

        domain_vulnerable = not dmarc_strong

        output = {
            'opcode': "test",
            'message': {
                'vulnerable': domain_vulnerable,
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
                    },
                },

            },
        }

        self.write_message(output)
