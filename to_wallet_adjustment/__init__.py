from odoo import api, SUPERUSER_ID
from . import models
from . import wizard
from . import tests


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env['res.company']._install_wallet_adjustment_journals()
