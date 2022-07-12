from odoo import fields, models


class View(models.Model):
    _inherit = 'ir.ui.view'

    type = fields.Selection(selection_add=[('viin_dashboard', "Dashboard")], ondelete={'viin_dashboard': 'cascade'})
