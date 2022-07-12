from odoo import models, fields, api


class HrContract(models.Model):
    _inherit = 'hr.contract'

    timesheet_approval = fields.Boolean(string='Timesheet Approval', compute='_compute_timesheet_approval', store=True,
                                        tracking=True, readonly=False,
                                        help="If enabled, timesheet entries of the employee of this contract during the contact's period"
                                        " will require approval. Otherwise, they will approved automatically.")

    @api.depends('department_id', 'job_id')
    def _compute_timesheet_approval(self):
        for r in self:
            r.timesheet_approval = True if r.job_id.timesheet_approval or r.department_id.timesheet_approval else False
