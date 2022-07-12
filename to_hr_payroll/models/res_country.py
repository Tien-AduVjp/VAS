from odoo import api, fields, models, _


class ResCountry(models.Model):
    _inherit = 'res.country'

    personal_tax_rule_progress_ids = fields.One2many('personal.tax.rule', 'country_id', string='Personal Tax Rules', ondelete='restrict')

