from odoo import models, fields, api


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    # begin override
    job_position_skills_required = fields.Boolean(tracking=True)
    # end override

