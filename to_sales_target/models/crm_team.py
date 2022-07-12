from odoo import fields, models, api


class CrmTeam(models.Model):
    _name = 'crm.team'
    _inherit = ['crm.team', 'sales.target.mixin']

    team_sales_target_ids = fields.One2many('team.sales.target', 'crm_team_id', string='Sales Targets')

    def get_target_by_period(self, start_date, end_date, states=('approved', 'done')):
        self.ensure_one()
        matched_target_ids = self.team_sales_target_ids.filtered(lambda target: target.end_date >= start_date \
                                                                 and target.start_date <= end_date \
                                                                 and target.state in states)
        target = matched_target_ids.get_target_sum(start_date, end_date)
        return target, matched_target_ids
