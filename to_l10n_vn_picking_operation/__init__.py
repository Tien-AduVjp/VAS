from odoo import api, SUPERUSER_ID
from . import models


def _restore_default_odoo_report_id(env):
    """If this module is uninstalled, the system will automatically restore Odoo's default report"""
    report_id = env.ref('stock.action_report_picking')
    report_id.write({'report_name': 'stock.report_picking',
                     'report_file': 'stock.report_picking_operations'})

def uninstall_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _restore_default_odoo_report_id(env)
