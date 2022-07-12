from dateutil.relativedelta import relativedelta

from odoo import fields, models

from .sale_order_line import PERIODS


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    subscription_state = fields.Selection(selection=[('create', 'Creation'), ('renew', 'Renewal'), ('upsell', 'Upselling')],
                                               string='Subscription Management',
                                               default='create',
                                               help="Creation: The Sales Order will generate subscriptions\n"
                                                    "Renewal: The Sales Order will replace the subscription's lines with its corresponding lines\n"
                                                    "Upselling: The Sales Order will add lines to the existing subscription")
    subscription_count = fields.Integer(string='Subscription Count', compute='_compute_subscription_count')

    def _compute_subscription_count(self):
        order_lines = self.env['sale.order.line'].search([('order_id', 'in', self.ids), ('subscription_id', '!=', False)])
        for r in self:
            r.subscription_count = len(order_lines.filtered(lambda l: l.order_id.id == r.id))

    def action_view_subscriptions(self):
        self.ensure_one()
        subscriptions = self.order_line.mapped('subscription_id')
        action = self.env.ref('to_sale_subscription.sale_subscription_action').read()[0]
        
        count = len(subscriptions)
        if count == 1:
            action['views'] = [(self.env.ref('to_sale_subscription.sale_subscription_view_form').id, 'form')]
            action['res_id'] = subscriptions.id
        elif count > 1:
            action['domain'] = [('id', 'in', subscriptions.ids)]
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    def _prepare_subscription_vals(self, template):
        self.ensure_one()
        vals = {
            'name': template.name,
            'template_id': template.id,
            'user_id': self.user_id.id,
            'team_id': self.team_id.id,
            'partner_id': self.partner_invoice_id.id,
            'description': self.note or template.description,
            'company_id': self.company_id.id,
            'pricelist_id': self.pricelist_id.id,
            'date_start': fields.Date.today(),
            'analytic_account_id': self.analytic_account_id.id,
            'payment_token_id': self.transaction_ids.get_last_transaction().payment_token_id.id if template.payment_mode in ('validate_send_payment', 'success_payment') else False
        }
        
        default_stage = self.env['sale.subscription.stage'].search([('in_progress', '=', True)], limit=1)
        if default_stage:
            vals['stage_id'] = default_stage.id
        # cacl the next date
        invoicing_period = relativedelta(**{PERIODS[template.recurring_rule_type]: template.recurring_interval})
        recurring_next_date = fields.Date.today() + invoicing_period
        vals['recurring_next_date'] = fields.Date.to_string(recurring_next_date)
        return vals

    def _update_existing_subscriptions(self):
        res = []
        for r in self:
            subscriptions = r.order_line.mapped('subscription_id').sudo()
            if subscriptions:
                res.append(subscriptions.ids)
                
                if r.subscription_state == 'renew':
                    subscriptions.wipe()
                    subscriptions.increment_period()
                    subscriptions.set_open()
                else:
                    r.subscription_state = 'upsell'
                
                for sub in subscriptions:
                    lines = r.order_line.filtered(lambda l: l.subscription_id.id == sub.id and l.product_id.recurring_invoice)
                    sub.write({
                        'line_ids': lines._prepare_update_subscription_line_vals_list(sub),
                        })
        return res

    def _generate_subscriptions(self):
        # create a subscription for each template with all the necessary lines
        res = []
        for r in self:
            templates = r._split_subscription_lines()
            for template in templates:
                values = r._prepare_subscription_vals(template)
                values['line_ids'] = templates[template]._prepare_subscription_line_data()
                subscription = self.env['sale.subscription'].sudo().create(values)
                subscription._onchange_date_start()
                templates[template].write({'subscription_id': subscription.id})
                subscription.message_post_with_view(
                    'mail.message_origin_link', values={'self': subscription, 'origin': r},
                    subtype_id=self.env.ref('mail.mt_note').id, author_id=self.env.user.partner_id.id
                )
                res.append(subscription.id)
        return res

    def _split_subscription_lines(self):
        """
        Split the order line according to subscription templates that must be created.
        :return dictionary of sale.order.line records grouped by subscription templates
            {
                'template1': order_lines1,
                'template2': order_lines2,
            }
        """
        self.ensure_one()
        res = dict()
        for template in self.order_line.filtered(lambda l: not l.subscription_id and l.product_id.subscription_template_id).mapped('product_id.subscription_template_id'):
            lines = self.order_line.filtered(lambda l: l.product_id.subscription_template_id == template)
            res[template] = lines
        return res

    def _action_confirm(self):
        res = super(SaleOrder, self)._action_confirm()
        self._update_existing_subscriptions()
        self._generate_subscriptions()
        return res

    def _get_payment_type(self, tokenize=False):
        if any(line.product_id.recurring_invoice for line in self.sudo().mapped('order_line')):
            return 'form_save'
        return super(SaleOrder, self)._get_payment_type(tokenize=tokenize)
