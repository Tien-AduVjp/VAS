from odoo import fields, models, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    affcode_id = fields.Many2one('affiliate.code', string="AffCode", readonly=True,
                                 copy=False, ondelete='restrict', index=True,
                                 domain="[('company_id','=',company_id)]",
                                 states={'draft': [('readonly', False)], 'sent': [('readonly', False)]})
    referrer_analysis_id = fields.Many2one('affiliate.referrer', string="Referrer", readonly=True,
        copy=False, ondelete='restrict', index=True)

    commission_ids = fields.One2many('affiliate.commission', 'order_id', string='Commissions')
    commission_ids_count = fields.Integer(string='Commission Count', compute='_compute_commission_ids_count', store=True)

    @api.depends('commission_ids')
    def _compute_commission_ids_count(self):
        for r in self:
            r.commission_ids_count = len(r.commission_ids)

    def _prepare_commission_data(self):
        self.ensure_one()
        line_ids = []
        for line in self.order_line:
            line_data = line._prepare_commission_line_data()
            if bool(line_data):
                line_ids.append((0, 0, line_data))
        if not line_ids:
            return {}

        return {
            'name': self.name,
            'affcode_id': self.affcode_id.id,
            'customer_id': self.partner_id.id,
            'partner_id': self.affcode_id.partner_id.id,
            'date': self.date_order,
            'order_id': self.id,
            'line_ids': line_ids,
            'currency_id': self.currency_id.id,
            'company_id': self.company_id.id
        }
        
    def _action_confirm(self):
        res = super(SaleOrder, self)._action_confirm()
        # create affiliate commission if any
        comm_vals_list = []
        for r in self.filtered(lambda so: so.affcode_id):
            comm_data = r._prepare_commission_data()
            if bool(comm_data):
                comm_vals_list.append(comm_data)
        if comm_vals_list:
            affiliate_commissions = self.env['affiliate.commission'].sudo().create(comm_vals_list)
            affiliate_commissions.action_confirm()
        return res

    def action_cancel(self):
        commission_ids = self.mapped('commission_ids')
        if commission_ids:
            commission_ids.action_cancel()
            commission_ids.action_draft()
            commission_ids.unlink()
        return super(SaleOrder, self).action_cancel()

    def action_view_commission(self):
        commission_ids = self.mapped('commission_ids')
        action = self.env.ref('to_affiliate.action_to_affiliate_com_tree_view').read()[0]

        if len(commission_ids) > 1:
            action['domain'] = [('id', 'in', commission_ids.ids)]
        elif len(commission_ids) == 1:
            action['views'] = [(self.env.ref('to_affiliate.to_affiliate_com_form_view').id, 'form')]
            action['res_id'] = commission_ids.ids[0]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action
