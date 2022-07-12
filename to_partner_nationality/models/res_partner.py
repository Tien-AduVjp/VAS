from odoo import fields,models

class ResPartner(models.Model):
    _inherit='res.partner'

    nationality_id = fields.Many2one('res.country', string="Nationality", tracking=True)
