from . import controllers
from . import models
from . import wizard

from odoo import api, SUPERUSER_ID


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env['res.company']._generate_sinvoice_config_params()
    env['res.company']._update_sinvoice_settings()
