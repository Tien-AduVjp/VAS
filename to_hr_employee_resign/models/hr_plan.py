from odoo import fields, models

class HrPlan(models.Model):
    _inherit = 'hr.plan'

    department_id = fields.Many2one('hr.department', string='Department')
    is_offboarding = fields.Boolean(string='Is OffBoarding')
