from . import models

from odoo import api, SUPERUSER_ID


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    companies = env['res.company'].search([])
    companies._generate_approval_request_type()
