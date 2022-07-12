from odoo import models, fields


class Project(models.Model):
    _inherit = 'project.project'

    timesheet_ids = fields.One2many('account.analytic.line', 'project_id', string="Timesheet")
