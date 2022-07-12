from odoo import api, SUPERUSER_ID, _

from . import models

def _generate_approval_request_type(env):
    companies = env['res.company'].search([])
    if companies:
        companies._generate_approval_request_type()


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _generate_approval_request_type(env)
