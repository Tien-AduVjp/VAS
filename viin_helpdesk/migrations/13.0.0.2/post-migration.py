# -*- coding: utf-8 -*-
from odoo import api, SUPERUSER_ID


def _activate_digest(env):
    default_digest = env.ref('digest.digest_digest_default')
    default_digest.write({
        'kpi_helpdesk_ticket_opened': True,
        'kpi_helpdesk_ticket_closed': True,
        })


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _activate_digest(env)

