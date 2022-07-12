from odoo import models, fields, api


class HrJob(models.Model):
    _inherit = 'hr.job'

    timesheet_approval = fields.Boolean(string='Timesheet Approval', compute='_compute_timesheet_approval', store=True,
                                        tracking=True, readonly=False,
                                        help="If enabled, timesheet entries of the employees of this job position"
                                        " will require approval. Otherwise, they will approved automatically.\n"
                                        "Note: this can be overridden by employees' contracts")

    @api.depends('department_id')
    def _compute_timesheet_approval(self):
        for r in self:
            r.timesheet_approval = r.department_id.timesheet_approval
