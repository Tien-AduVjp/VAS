from odoo import fields, models


class HelpdeskTicketType(models.Model):
    _name = 'helpdesk.ticket.type'
    _description = 'Helpdesk Ticket Type'
    _order = 'sequence'

    name = fields.Char(string='Name', required=True, translate=True)
    description = fields.Text(string='Description', translate=True)
    sequence = fields.Integer(string='Sequence')

    _sql_constraints = [
        ('ticket_type_name_uniq',
         'unique(name)',
         "The name of Ticket type must be unique!"),
    ]
