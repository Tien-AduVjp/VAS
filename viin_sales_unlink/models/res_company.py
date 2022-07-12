from odoo import models, fields

class ResCompany(models.Model):
    _inherit = 'res.company'

    prevent_unlink_sales_having_invoices = fields.Boolean(string='Disallow to unlink SO/SO line having Invoices', default=False)
