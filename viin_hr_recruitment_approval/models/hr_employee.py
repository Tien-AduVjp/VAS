from odoo import models, fields


class HREmployee(models.AbstractModel):
    _inherit = 'hr.employee.base'

    approval_id = fields.Many2one('approval.request', string='Recruitment Request', index=True)
