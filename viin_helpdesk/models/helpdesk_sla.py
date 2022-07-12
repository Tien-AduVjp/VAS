from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class HelpdeskSLA(models.Model):
    _name = 'helpdesk.sla'
    _description = 'Helpdesk SLA'
    _order = 'name'

    name = fields.Char(string='Name', required=True, translate=True)
    description = fields.Text(string='Description', translate=True)
    team_id = fields.Many2one('helpdesk.team', string='Helpdesk Team', required=True)
    active = fields.Boolean(string='Active', default=True)
    minimum_priority = fields.Selection([
        ('0', 'All'),
        ('1', 'Low Priority'),
        ('2', 'High Priority'),
        ('3', 'Urgent')
    ], string='Minimum Priority', default='0')
    ticket_type_ids = fields.Many2many('helpdesk.ticket.type', string='Ticket Types')
    tag_ids = fields.Many2many('helpdesk.tag', string='Ticket Tags')
    stage_id = fields.Many2one('helpdesk.stage', string='Reach Stage', required=True, domain="[('team_ids', 'in', team_id)]",
                               help="Minimum stage a ticket needs to reach in order to satisfy this SLA policy.")
    time_hours = fields.Float(string='Hours', default=0, required=True, help="Hours to reach given stage based on ticket creation date")
    ticket_ids = fields.Many2many('helpdesk.ticket', 'helpdesk_ticket_sla_rel', string="Tickets", store=True, copy=False, readonly=True)
    tickets_count = fields.Integer(string='Ticket count', compute='_compute_ticket_count')

    @api.constrains('team_id', 'minimum_priority', 'ticket_type_ids', 'tag_ids', 'stage_id', 'time_hours')
    def _check_slas(self):
        slas = self.env['helpdesk.sla'].sudo().search([('id', 'not in', self.ids),('team_id', 'in', self.team_id.ids), ('stage_id', 'in', self.stage_id.ids)])
        for r in self:
            for sla in slas.filtered(lambda s: s.team_id == r.team_id and s.stage_id == r.stage_id):
                if r.minimum_priority == sla.minimum_priority and \
                   r.ticket_type_ids == sla.ticket_type_ids and \
                   r.tag_ids == sla.tag_ids and \
                   r.time_hours == sla.time_hours:
                    raise ValidationError(_("Conditions must not overlap with other SLAs"))
            slas |= r

    @api.depends('ticket_ids')
    def _compute_ticket_count(self):
        for r in self:
            r.tickets_count = len(r.ticket_ids)

    def action_open_tickets(self):
        self.ensure_one()

        return {
            'name': _('Tickets'),
            'view_type': 'form',
            'view_mode': 'kanban,tree,form,pivot,calendar,graph',
            'res_model': 'helpdesk.ticket',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', self.ticket_ids.ids)],
        }
