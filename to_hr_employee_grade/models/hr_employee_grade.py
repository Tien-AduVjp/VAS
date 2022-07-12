from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class EmployeeGrade(models.Model):
    _name = 'hr.employee.grade'
    _description = "Employee Grade"
    _inherit = ['mail.thread']
    _order = "sequence"

    name = fields.Char(string='Name', required=True, index=True, translate=True)
    active = fields.Boolean('Active', default=True)
    parent_id = fields.Many2one('hr.employee.grade', string='Parent',
                                domain="['&', ('department_id', '=', department_id), '|', ('company_id', '=', False), ('company_id', '=', current_company_id)]")
    sequence = fields.Integer(string='Sequence', compute='_compute_sequence', store=True, index=True)
    recursive_parent_ids = fields.Many2many('hr.employee.grade', 'hr_employee_grade_parent_rel', 'grade_id', 'parent_id',
                                           compute='_compute_recursive_parent_ids', store=True,
                                           string='Recursive Parents',
                                           help="Direct and indirect parents")
    child_ids = fields.One2many('hr.employee.grade', 'parent_id', string='Lower Grade', readonly=True)
    recursive_child_ids = fields.Many2many('hr.employee.grade', 'hr_employee_grade_parent_rel', 'parent_id', 'grade_id', readonly=True,
                                           string='Recursive Children',
                                           help="Direct and indirect children")
    employee_ids = fields.One2many('hr.employee', 'grade_id', string='Employees', groups='base.group_user')
    employees_count = fields.Integer(string='Employees Count', compute='_compute_employees_count', compute_sudo=True,
        help="Number of employees currently occupying this grade.")
    department_id = fields.Many2one('hr.department', string='Department',
                                    domain="['|', ('company_id', '=', False), ('company_id', '=', current_company_id)]")
    parent_path = fields.Char(string='Parent Path')
    description = fields.Text(string='Grade Description')
    company_id = fields.Many2one('res.company', string='Company')

    _sql_constraints = [
        ('name_uniq', 'unique(name, company_id, department_id)', 'The name of the grade must be unique per department in company!'),
    ]

    @api.constrains('department_id')
    def _check_department(self):
        self.employee_ids._check_grade_department()

    @api.depends('parent_id.sequence', 'child_ids.sequence')
    def _compute_sequence(self):
        for r in self:
            if not r.parent_id:
                r.sequence = 10
            else:
                r.sequence = r.parent_id.sequence - 1

    @api.depends('parent_id', 'child_ids.parent_id')
    def _compute_recursive_parent_ids(self):
        for r in self:
            r.recursive_parent_ids = r._get_recursive_parents()

    @api.depends('employee_ids.grade_id')
    def _compute_employees_count(self):
        employee_data = self.env['hr.employee'].read_group([('grade_id', 'in', self.ids)], ['grade_id'], ['grade_id'])
        result = dict((data['grade_id'][0], data['grade_id_count']) for data in employee_data)
        for r in self:
            r.employees_count = result.get(r.id, 0)

    @api.constrains('parent_id')
    def _check_category_grade(self):
        if not self._check_recursion():
            raise ValidationError(_('You cannot create recursive grades.'))
        return True

    @api.constrains('parent_id', 'department_id')
    def _check_parent_in_department(self):
        for r in self:
            if r.parent_id and r.department_id != r.parent_id.department_id:
                    raise ValidationError(_("The parent grade must be in the same department with this grade: %s") % r.name)

    def _get_recursive_parents(self):
        parents = self.parent_id
        for parent in self.parent_id:
            parents |= parent._get_recursive_parents()
        return parents

    @api.model
    def _get_grades_without_department(self):
        return self.env['hr.employee.grade'].search([('department_id', '=', False)])

    def action_view_employees(self):
        if self.env.user.has_group('hr.group_hr_user'):
            action_xmlid = 'hr.open_view_employee_list_my'
        else:
            action_xmlid = 'hr.hr_employee_public_action'
        action = self.env['ir.actions.act_window']._for_xml_id(action_xmlid)
        # override to get rid off the default context
        action['context'] = {
            'default_grade_id': self.id,
            'default_company_id': self.company_id.id
            }
        action['domain'] = [('grade_id', 'in', self.ids)]
        return action
