from odoo import models, fields, api


class HrDepartment(models.Model):
    _inherit = 'hr.department'

    timesheet_approval = fields.Boolean(string='Timesheet Approval', compute='_compute_timesheet_approval', store=True,
                                        tracking=True, readonly=False,
                                        help="If enabled, timesheet entries of the employees of this department"
                                        " will require approval. Otherwise, they will approved automatically.\n"
                                        "Note: this can be overridden by employees' contracts")

    @api.depends('parent_id')
    def _compute_timesheet_approval(self):
        for r in self:
            r.timesheet_approval = True if r.parent_id else False
