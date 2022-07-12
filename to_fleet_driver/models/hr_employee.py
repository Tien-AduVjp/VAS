from odoo import fields, models


class HREmployee(models.Model):
    _inherit = 'hr.employee'

    is_driver = fields.Boolean(string='Is Driver', related='address_home_id.is_driver', store=True, groups='hr.group_hr_user')
