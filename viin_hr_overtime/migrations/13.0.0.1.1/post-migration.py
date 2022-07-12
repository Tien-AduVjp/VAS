# -*- coding: utf-8 -*-
from odoo import api, SUPERUSER_ID


def _fix_ot_rule_code(env):
    xml_ids = [
        'rule_code_othol0006',
        'rule_code_othol0618',
        'rule_code_othol1822',
        'rule_code_othol2224',
        'rule_code_otholsat0006',
        'rule_code_otholsat0612',
        'rule_code_otholsat1218',
        'rule_code_otholsat1822',
        'rule_code_otholsat2224',
        'rule_code_otholsun0006',
        'rule_code_otholsun0612',
        'rule_code_otholsun1218',
        'rule_code_otholsun1822',
        'rule_code_otholsun2224'
        ]
    rule_codes = env['hr.overtime.rule.code']
    for xml_id in xml_ids:
        rule_codes |= env.ref('viin_hr_overtime.%s' % xml_id)
    if rule_codes:
        rule_codes.write({
            'holiday': True
            })


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _fix_ot_rule_code(env)

