from odoo import fields, models, _


class Partner(models.Model):
    _inherit = 'res.partner'

    ticket_ids = fields.One2many('helpdesk.ticket', 'partner_id', string='Tickets')
    tickets_count = fields.Integer(string='Tickets Count', compute='_compute_tickets_count')

    def _compute_tickets_count(self):
        tickets_data = self.env['helpdesk.ticket'].read_group([('partner_id', 'in', self.ids)], ['partner_id'], ['partner_id'])
        mapped_data = dict([(dict_data['partner_id'][0], dict_data['partner_id_count']) for dict_data in tickets_data])
        for r in self:
            r.tickets_count = mapped_data.get(r.id, 0)

    def action_view_tickets(self):
        self.ensure_one()
        
        ctx = dict(self.env.context or {})
        ctx.update({
            'default_partner_id': self.id,
            })
        
        return {
            'name': _('Tickets'),
            'view_type': 'form',
            'view_mode': 'kanban,tree,form,pivot,calendar,graph',
            'res_model': 'helpdesk.ticket',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'context': ctx,
            'domain': [('id', 'in', self.ticket_ids.ids)],
        }
