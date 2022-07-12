from odoo import fields, models, api


class ResUsers(models.Model):
    _name = 'res.users'
    _inherit = ['res.users', 'sales.target.mixin']

    personal_sales_target_ids = fields.One2many('personal.sales.target', 'sale_person_id', string='Personal Sales Target')

    def get_target_by_period(self, start_date, end_date, states=('approved', 'done')):
        self.ensure_one()
        matched_target_ids = self.personal_sales_target_ids.filtered(lambda target: target.end_date >= start_date \
                                                                     and target.start_date <= end_date \
                                                                     and target.state in states)
        target = matched_target_ids.get_target_sum(start_date, end_date)
        return target, matched_target_ids
