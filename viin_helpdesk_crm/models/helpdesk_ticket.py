from odoo import fields, models


class Ticket(models.Model):
    _inherit = 'helpdesk.ticket'

    lead_id = fields.Many2one('crm.lead', string='Lead/Opportunity')
