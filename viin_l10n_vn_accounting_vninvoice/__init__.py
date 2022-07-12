from odoo import api, SUPERUSER_ID
from . import models
from . import wizard


def _update_einvoice_services(env):
    sinvoice_services = env['einvoice.service'].search([('module_id', '=', env.ref('base.module_viin_l10n_vn_accounting_vninvoice').id)])
    sinvoice_services.write({'provider': 'vninvoice'})

def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _update_einvoice_services(env)
