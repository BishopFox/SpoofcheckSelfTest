# -*- coding: utf-8 -*-
"""
@author: lunarca
Copyright 2017
"""

import os
import requests
import logging

from tasks import selftest_task_queue

from emailprotectionslib import spf as spflib
from emailprotectionslib import dmarc as dmarclib


@selftest_task_queue.task
def email_spoofing_analysis(domain):
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

    return output


@selftest_task_queue.task
def check_recaptcha_solution(user_solution, ip_address):
    payload = {
        "secret": os.environ["RECAPTCHA_SECRET_KEY"],
        "response": user_solution,
        "remoteip": ip_address,
    }

    recaptcha_response = requests.post("https://www.google.com/recaptcha/api/siteverify", data=payload)

    logging.debug("[RECAPTCHA Response] " + recaptcha_response.text)
    return recaptcha_response.json()["success"]
