from . import models
from . import wizard
from . import controllers
from odoo import SUPERUSER_ID, api

def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env['res.company']._generate_vninvoice_config_params()