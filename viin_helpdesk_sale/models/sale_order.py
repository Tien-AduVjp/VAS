from odoo import fields, models, api, _


class SaleOrder(models.Model):
    _inherit = "sale.order"

    ticket_ids = fields.One2many('helpdesk.ticket', 'sale_order_id', string='Tickets')
    tickets_count = fields.Integer(string='Tickets Count', compute='_compute_tickets_count')

    @api.model
    def _get_default_sale_helpdesk_team(self):
        return self.env['helpdesk.team'].sudo().search([
            ('name', '=', _('Customer Support')),
            ('company_id', '=', self.env.company.id)], limit=1) or self.env.company.default_helpdesk_team_id

    def _compute_tickets_count(self):
        orders_data = self.env['helpdesk.ticket'].read_group([('sale_order_id', 'in', self.ids)], ['sale_order_id'], ['sale_order_id'])
        mapped_data = dict([(dict_data['sale_order_id'][0], dict_data['sale_order_id_count']) for dict_data in orders_data])
        for r in self:
            r.tickets_count = mapped_data.get(r.id, 0)

    def action_view_tickets(self):
        self.ensure_one()

        ctx = dict(self.env.context or {})
        ctx.update({
            'default_sale_order_id': self.id,
            })
        teams = self.mapped('ticket_ids.team_id') or self._get_default_sale_helpdesk_team()
        if len(teams) == 1:
            ctx.update({
                'search_default_team_id': teams[0].id,
                'default_team_id': teams[0].id,
                })
        return {
            'name': _('Tickets'),
            'view_type': 'form',
            'view_mode': 'kanban,tree,form,pivot,calendar,graph',
            'res_model': 'helpdesk.ticket',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', self.ticket_ids.ids)],
            'context': ctx,
        }
