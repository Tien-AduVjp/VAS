from odoo import fields, models, _


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    subscription_ids = fields.One2many('sale.subscription', 'analytic_account_id', string='Subscriptions')
    subscription_count = fields.Integer(string='Subscription Count', compute='_compute_subscription_count')

    def _compute_subscription_count(self):
        subscription_data = self.env['sale.subscription'].read_group([('analytic_account_id', 'in', self.ids)],
                                                                     ['analytic_account_id'],
                                                                     ['analytic_account_id'])
        mapped_data = dict([(s['analytic_account_id'][0], s['analytic_account_id_count']) for s in subscription_data])
        for r in self:
            r.subscription_count = mapped_data.get(r.id, 0)

    def action_view_subscriptions(self):
        result = {
            'name': _('Subscriptions'),
            'type': 'ir.actions.act_window',
            'res_model': 'sale.subscription',
            'views': [[False, 'tree'], [False, 'form']],
            'domain': [['id', 'in', self.mapped('subscription_ids').ids]],
            'context': {'create': False},
        }
        if len(self.mapped('subscription_ids')) == 1:
            result['views'] = [(False, 'form')]
            result['res_id'] = self.mapped('subscription_ids').id
        return result
