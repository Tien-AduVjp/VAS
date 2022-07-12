from odoo import api, SUPERUSER_ID

from . import models


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    companies = env['res.company'].search([])
    companies._generate_approval_request_type()
