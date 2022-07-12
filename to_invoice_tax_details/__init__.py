from odoo import api, SUPERUSER_ID
from . import models

def _reset_show_line_subtotals_tax_selection(env):
    env['res.config.settings'].search([('show_line_subtotals_tax_selection', '=', 'tax_details')]).write({
        'show_line_subtotals_tax_selection': 'tax_excluded'
        })
    env['ir.config_parameter'].search([('key', '=', 'account.show_line_subtotals_tax_selection'), ('value', '=', 'tax_details')]).write({
        'value': 'tax_excluded'
        })

def uninstall_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _reset_show_line_subtotals_tax_selection(env)
