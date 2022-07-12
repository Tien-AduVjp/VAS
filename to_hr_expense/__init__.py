from odoo import api, SUPERUSER_ID

from . import models
from . import wizard

def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env['hr.expense']._update_to_invoice_status_for_existing_expenses()