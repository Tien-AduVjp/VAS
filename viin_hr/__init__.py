from odoo import api, SUPERUSER_ID

from . import models


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env['res.partner'].with_context(active_test=False).search([])._compute_employee_ids()
