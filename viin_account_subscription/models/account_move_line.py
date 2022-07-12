from odoo import models, fields, api
from odoo.tools import format_datetime


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    subscription_from = fields.Datetime(string='Subscription From')
    subscription_to = fields.Datetime(string='Subscription To')
    subscription_hours = fields.Float(compute='_compute_subscription_hours')

    _sql_constraints = [
        ('check_subscription_from_to',
         'CHECK(subscription_to >= subscription_from)',
         "Subscription To must be later than or equal to the Subscription From!"),
    ]

    @api.depends('subscription_from', 'subscription_to')
    def _compute_subscription_hours(self):
        for r in self:
            if r.subscription_from and r.subscription_to:
                diff = r.subscription_to - r.subscription_from
                r.subscription_hours = diff.days * 24 + diff.seconds / 3600
            else:
                r.subscription_hours = 0.0

    def _get_subscription_explanation(self):
        self.ensure_one()
        name = ''
        if self.subscription_from and self.subscription_to:
            tz = self.partner_id.commercial_partner_id.tz or self.env.context.get('tz') or 'UTC'
            name += '\n[%s -> %s] (%s)' % (
                format_datetime(self.env, self.subscription_from, tz),
                format_datetime(self.env, self.subscription_to, tz),
                tz
                )
        return name

    def _get_computed_name(self):
        name = super(AccountMoveLine, self)._get_computed_name()
        if self.subscription_from and self.subscription_to:
            name += self._get_subscription_explanation()
        return name
