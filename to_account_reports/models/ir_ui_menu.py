from odoo import models, fields

class IrUiMenu(models.Model):
    _inherit = 'ir.ui.menu'

    chart_template_id = fields.Many2one('account.chart.template', help='The chart template for the menu (if any)')
