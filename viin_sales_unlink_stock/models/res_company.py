from odoo import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    prevent_unlink_sales_having_pickings = fields.Boolean(string='Disallow to unlink SO having Stock Transfers', default=False)
