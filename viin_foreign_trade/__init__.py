from odoo import api, SUPERUSER_ID

from . import models
from . import wizard

def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env['account.journal'].create_imex_tax_journals()
    env['account.journal'].create_import_landed_cost_tax_journals()
