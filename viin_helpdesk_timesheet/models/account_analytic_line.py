from odoo import fields, models


class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'
    
    ticket_id = fields.Many2one('helpdesk.ticket', string='Helpdesk Ticket')