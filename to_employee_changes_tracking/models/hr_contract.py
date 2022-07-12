from odoo import fields, models


class Contract(models.Model):
    _inherit = 'hr.contract'

    department_id = fields.Many2one(tracking=True)
    job_id = fields.Many2one(tracking=True)
    resource_calendar_id = fields.Many2one(tracking=True)
