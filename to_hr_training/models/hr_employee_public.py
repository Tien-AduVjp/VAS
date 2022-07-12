from odoo import api, fields, models


class HrEmployeePublic(models.Model):
    _inherit = 'hr.employee.public'

    training_line_ids = fields.One2many('hr.employee.training.line', 'employee_id', string='Employee Training', compute='_compute_training_line_ids', readonly=True, compute_sudo=True)

    @api.depends('job_id', 'grade_id')
    def _compute_training_line_ids(self):
        """
        This method compute field 'slide_channel_id and' and 'require_hour'.
        Field 'training_line_ids' will be calculated by the course according to that employee's grade/job and 
        all below grade of an employee.
        """
        employees = self.env['hr.employee'].sudo().browse(self.ids)
        for r in self:
            if r.show_required_course:
                r.training_line_ids = employees.filtered(lambda e: e.id == r.id).training_line_ids
            else:
                r.training_line_ids = False
