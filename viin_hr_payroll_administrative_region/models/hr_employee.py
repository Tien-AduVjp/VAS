from odoo import fields, models


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    administrative_region_id = fields.Many2one('administrative.region', string='Administrative Region', groups="hr.group_hr_user")
