from odoo import models, fields

class ResCompany(models.Model):
    _inherit = 'res.company'

    prevent_unlink_related_invoices = fields.Boolean(string='Disallow to unlink SO/SO line relating Invoices', default=False)
