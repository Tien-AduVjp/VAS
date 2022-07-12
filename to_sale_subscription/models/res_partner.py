from odoo import fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    subscription_count = fields.Integer(string='Subscriptions', compute='_compute_subscription_count')

    def _compute_subscription_count(self):
        subscription_data = self.env['sale.subscription'].read_group([('partner_id', 'in', self.ids)],
                                                                     ['partner_id'],
                                                                     ['partner_id'])
        mapped_data = dict([(s['partner_id'][0], s['partner_id_count']) for s in subscription_data])
        for r in self:
            r.subscription_count = mapped_data.get(r.id, 0)
