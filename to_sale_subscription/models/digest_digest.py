from odoo import fields, models, _
from odoo.exceptions import AccessError


class Digest(models.Model):
    _inherit = 'digest.digest'

    kpi_subscription_in_progress = fields.Boolean('In Progress Subscriptions')
    kpi_subscription_in_progress_value = fields.Integer(compute='_compute_kpi_subscription_in_progress_value')
    kpi_subscription_closed = fields.Boolean('Closed Subscriptions')
    kpi_subscription_closed_value = fields.Integer(compute='_compute_kpi_subscription_closed_value')

    def _check_access_right(self):
        if not self.env.user.has_group('to_sale_subscription.group_sale_subscription_view'):
            raise AccessError(_("Do not have access, skip this data for user's digest email"))

    def _compute_kpi_subscription_in_progress_value(self):
        self._check_access_right()
        for r in self:
            start, end, company = r._get_kpi_compute_parameters()
            in_progress_subscription = self.env['sale.subscription'].search_count([
                ('create_date', '>=', start),
                ('create_date', '<', end),
                ('company_id', '=', company.id),
                ('stage_id.in_progress', '=', True), ('to_renew', '=', False),
            ])
            r.kpi_subscription_in_progress_value = in_progress_subscription

    def _compute_kpi_subscription_closed_value(self):
        self._check_access_right()
        for r in self:
            start, end, company = r._get_kpi_compute_parameters()
            closed_subscription = self.env['sale.subscription'].search_count([
                ('create_date', '>=', start),
                ('create_date', '<', end),
                ('company_id', '=', company.id),
                ('stage_id.in_progress', '=', False),
            ])
            r.kpi_subscription_closed_value = closed_subscription

    def compute_kpis_actions(self, company, user):
        res = super(Digest, self).compute_kpis_actions(company, user)
        res['kpi_subscription_in_progress'] = 'to_sale_subscription.sale_subscription_action&menu_id=%s' % self.env.ref('to_sale_subscription.menu_sale_subscription_action').id
        return res
