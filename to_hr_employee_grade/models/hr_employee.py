from odoo import models, fields


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    # override
    grade_id = fields.Many2one(ondelete='restrict', tracking=True)
