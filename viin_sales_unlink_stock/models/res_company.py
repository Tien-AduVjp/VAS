from odoo import models, fields

class ResCompany(models.Model):
    _inherit = 'res.company'

    prevent_unlink_related_pickings = fields.Boolean(string='Disallow to unlink SO relating Pickings', default=False)
