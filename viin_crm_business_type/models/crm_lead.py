from odoo import fields, models


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    business_type_id = fields.Many2one('res.partner.business.type', string='Business Type')
