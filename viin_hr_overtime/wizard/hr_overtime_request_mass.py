from odoo import models, fields, api, _
from odoo.exceptions import UserError


class HrOvertimeRequestMass(models.TransientModel):
    _name = 'hr.overtime.request.mass'
    _description = 'Mass Overtime Request Wizard'

    @api.model
    def _default_mode(self):
        if not self.env.user.has_group('viin_hr_overtime.group_overtime_officer'):
            mode = 'employee'
        else:
            mode = 'department'
        return mode

    mode = fields.Selection([
        ('employee', 'By Employee'),
        ('department', 'By Department'),
        ('company', 'By Company'),
        ], string='Mode', required=True, default=_default_mode, groups="viin_hr_overtime.group_overtime_officer")
    reason_id = fields.Many2one('hr.overtime.reason', string='Reason', required=True)
    company_ids = fields.Many2many('res.company', string='Companies', default=lambda self: self.env.companies, required=True)
    department_ids = fields.Many2many('hr.department', string='Departments', compute='_compute_department_ids', store=True, readonly=False)
    employee_ids = fields.Many2many('hr.employee', string='Employees', compute='_compute_employee_ids', store=True, readonly=False)
    line_ids = fields.One2many('hr.overtime.request.mass.line', 'overtime_request_mass_id', string='HR Overtime Request Mass Lines')

    @api.depends('mode', 'company_ids')
    def _compute_department_ids(self):
        departments = self.env['hr.department'].search(['|', ('company_id', '=', False), ('company_id', 'in', self.company_ids.ids)])
        for r in self:
            if r.mode == 'company':
                r.department_ids = [(6, 0, departments.filtered(lambda dep: not dep.company_id or dep.company_id.id in r.company_ids.ids).ids)]
            else:
                user_departments = self.env.user.department_id
                if r.mode == 'department' and user_departments:
                    user_departments |= departments.filtered_domain([('id', 'child_of', user_departments.ids)])
                r.department_ids = [(6, 0, user_departments.ids)]

    @api.depends('mode', 'company_ids', 'department_ids')
    def _compute_employee_ids(self):
        for r in self:
            employee_obj = self.env['hr.employee']
            if r.mode == 'company':
                r.employee_ids = [(6, 0, employee_obj.search(['|', ('company_id', '=', False), ('company_id', 'in', r.company_ids.ids)]).ids)]
            elif r.mode == 'department':
                r.employee_ids = [(6, 0, employee_obj.sudo().search([('department_id', 'in', r.department_ids.ids)]).ids)]
            else:
                r.employee_ids = [(6, 0, employee_obj.search(self.env['hr.overtime.plan']._get_employee_domain()).ids)]

    def _generate_overtime_plans(self):
        self.ensure_one()
        if not self.line_ids:
            raise UserError(_("No schedule given. Please input schedule first."))
        vals_list = []
        for company in self.company_ids:
            for employee in self.employee_ids.filtered(lambda emp: not emp.company_id or emp.company_id == company):
                for vals in self.line_ids._prepare_overtime_plan_vals_list():
                    vals.update({
                        'employee_id': employee.id,
                        'company_id': company.id
                        })
                    vals_list.append(vals)
        return self.env['hr.overtime.plan'].create(vals_list)
    
    def action_schedule(self):
        self.ensure_one()
        plans = self._generate_overtime_plans()
        action = self.env.ref('viin_hr_overtime.action_hr_overtime_plan')
        result = action.read()[0]
        result['context'] = {}
        result['domain'] = "[('id', 'in', %s)]" % str(plans.ids)
        return result
            
