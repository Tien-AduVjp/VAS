from odoo import models, fields, api
from odoo.tools import groupby
from odoo.osv import expression


class HrEmployeeBase(models.AbstractModel):
    _inherit = "hr.employee.base"

    show_required_course = fields.Boolean('Show Required Course', compute='_compute_show_required_course',
                                          help="Conditions to view the required courses of a certain employee in the employee directory")

    def _compute_show_required_course(self):
        is_hr_user = self.env.user.has_group('hr.group_hr_user')
        for r in self:
            manager = r.parent_id.user_id.id
            if r.env.user.id == (r.user_id.id or manager) or is_hr_user:
                r.show_required_course = True
            else:
                r.show_required_course = False


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    training_line_ids = fields.One2many('hr.employee.training.line', 'employee_id', string='Employee Training',
                                        compute='_compute_training_line_ids', store=True)

    @api.depends('job_id', 'job_id.require_training_ids', 'grade_id', 'grade_id.require_training_ids')
    def _compute_training_line_ids(self):
        """
        This method compute field 'slide_channel_id and' and 'require_hour'.
        Field 'training_line_ids' will be calculated by the course according to that employee's grade/job and 
        all below grade of an employee.
        """
        for r in self:
            vals_list = [(3, line.id) for line in r.training_line_ids]
            domain1 = [('job_id', '!=', False), ('job_id', '=', r.job_id.id)]
            domain2 = [('grade_id', 'child_of', r.grade_id.id)]
            if r.job_id and r.grade_id:
                domain = expression.OR([domain1, domain2])
            elif r.job_id:
                domain = domain1
            elif r.grade_id:
                domain = domain2
            else:
                domain = False
            if domain:
                data = r.env['hr.require.training'].search(domain)
                grouped_data = groupby(data, key=lambda d: d.slide_channel_id.id)  # Group all overlapping courses
                for channel_id, lines in grouped_data:
                    line_ids = self.env['hr.require.training'].concat(*lines)
                    vals_list.append((0, 0, line_ids._prepare_course_line_data()))
            r.training_line_ids = vals_list
