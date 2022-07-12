from odoo import models, fields


class SaleSubscriptionWizard(models.TransientModel):
    _name = 'sale.subscription.wizard'
    _description = 'Sales Subscription Wizard'

    def _default_subscription(self):
        return self.env['sale.subscription'].browse(self._context.get('active_id'))

    subscription_id = fields.Many2one('sale.subscription', string='Subscription', required=True, default=_default_subscription, ondelete='cascade')
    option_lines = fields.One2many('sale.subscription.wizard.option', 'wizard_id', string='Options')
    date_from = fields.Date('Discount Date', default=fields.Date.today,
                            help="The discount on a sales order will be computed based on the ratio between "
                                 "the full invoicing period of the subscription and the period between this date and the "
                                 "next invoicing date.")

    def action_create_sale_order(self):
        fpos_id = self.env['account.fiscal.position'].get_fiscal_position(self.subscription_id.partner_id.id)
        sale_order_obj = self.env['sale.order']
        team = self.env['crm.team']._get_default_team_id(user_id=self.subscription_id.user_id.id)
        new_order_vals = {
            'partner_id': self.subscription_id.partner_id.id,
            'analytic_account_id': self.subscription_id.analytic_account_id.id,
            'team_id': team and team.id,
            'pricelist_id': self.subscription_id.pricelist_id.id,
            'fiscal_position_id': fpos_id,
            'subscription_state': 'upsell',
            'origin': self.subscription_id.code,
        }
        # we don't override the default if no payment terms has been set on the customer
        if self.subscription_id.partner_id.property_payment_term_id:
            new_order_vals['payment_term_id'] = self.subscription_id.partner_id.property_payment_term_id.id
        order = sale_order_obj.create(new_order_vals)
        for line in self.option_lines:
            self.subscription_id.partial_invoice_line(order, line, date_from=self.date_from)
        order.order_line._compute_tax_id()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'sale.order',
            'views': [[False, 'form']],
            'res_id': order.id,
        }

    def action_add_lines(self):
        for r in self:
            vals = r._prepare_subscription_lines()
            r.subscription_id.sudo().write({'line_ids': vals})
        return True

    def _prepare_subscription_lines(self):
        vals_list = []
        for line in self.option_lines:
            vals = False
            for sub_line in self.subscription_id.line_ids.filtered(lambda l: l.product_id == line.product_id and l.uom_id == line.uom_id):
                vals = (1, sub_line.id, {'quantity': sub_line.quantity + line.quantity})
            if not vals:
                vals = (0, 0, {'product_id': line.product_id.id,
                                   'name': line.name,
                                   'quantity': line.quantity,
                                   'uom_id': line.uom_id.id,
                                   'price_unit': self.subscription_id.pricelist_id.with_context({'uom': line.uom_id.id}).get_product_price(line.product_id, 1, False)
                                   })
            vals_list.append(vals)
        return vals_list
