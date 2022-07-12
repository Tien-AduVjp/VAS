from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class HrRole(models.Model):
    _name = 'hr.role'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "HR Role"

    name = fields.Char(string='Name', required=True, translate=True,
                       help="E.g. Product Developer, Accountant, Consultant, QA Specialist, QC Specialists, etc")
    department_id = fields.Many2one('hr.department', string='Department',
                                    domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]",
                                    help="Once specified, the role is ONLY available for the selected department. In most cases,"
                                    " this field is preferred to be left blank.")
    company_id = fields.Many2one('res.company', string='Company',
                                 help="Once specified, the role is ONLY available for the selected company.",
                                 default=lambda self: self.env.company)
    description = fields.Html(string='Description', translate=True)
    employee_ids = fields.One2many('hr.employee', 'role_id', string='Employees', readonly=True, help="All the employees that are currently set at this role.")
    employees_count = fields.Integer(string='Employees Count', compute='_compute_employees_count', compute_sudo=True)
    active = fields.Boolean(default=True)

    @api.constrains('department_id')
    def _check_department(self):
        self.employee_ids._check_role_department()

    def _compute_employees_count(self):
        employees_data = self.env['hr.employee'].read_group([('role_id', 'in', self.ids)], ['role_id'], ['role_id'])
        mapped_data = dict([(dict_data['role_id'][0], dict_data['role_id_count']) for dict_data in employees_data])
        for r in self:
            r.employees_count = mapped_data.get(r.id, 0)

    @api.model
    def _get_roles_without_department(self):
        return self.env['hr.role'].search([('department_id', '=', False)])

    def action_view_employees(self):
        if self.env.user.has_group('hr.group_hr_user'):
            action_xmlid = 'hr.open_view_employee_list_my'
        else:
            action_xmlid = 'hr.hr_employee_public_action'
        action = self.env['ir.actions.act_window']._for_xml_id(action_xmlid)
        # override to get rid off the default context
        ctx = dict(self._context or {})
        ctx.update({
            'default_role_id': self[:1].id,
            'default_department_id': self.department_id[:1].id,
            'default_company_id': self.company_id[:1].id,
            })
        action['context'] = ctx
        domain = [('role_id', 'in', self.ids)]
        if 'grade_id' in ctx:
            domain.append(('grade_id', '=', ctx['grade_id']))
        action['domain'] = domain
        return action
