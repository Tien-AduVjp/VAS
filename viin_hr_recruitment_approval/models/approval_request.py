from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ApprovalRequest(models.Model):
    _inherit = 'approval.request'

    demand_department_id = fields.Many2one('hr.department',
                                    string='Demand Department',
                                    readonly=True, states={'draft':[('readonly', False)]},
                                    default=lambda self: self.env.user.employee_id.department_id,
                                    index=True
                                    )
    can_change_demand_dept = fields.Boolean(compute='_compute_can_change_demand_dept', string='Can Change Demand Department', help="Technical field to improve UX")
    job_id = fields.Many2one('hr.job', string='Requested Position',
                             domain="[('department_id', '=', demand_department_id)]",
                             readonly=True, states={'draft':[('readonly', False)]},
                             help="The Job Position you expected to get more hired."
                             )
    # TODO: Feature convert job_tmp to job_id is deprecated, please remove job_tmp field in v15.
    job_tmp = fields.Char(string='Job Title',
                          readonly=True, states={'draft':[('readonly', False)]},
                          help='If you don\'t select the requested position in the field above, you must specify a Job Title here. Upon this request is approved, the system can automatically create a new Job position and attach it to this request.')
    no_of_hired_employee = fields.Integer('Hired Employees',
                                          tracking=True,
                                          compute='_compute_count_dept_employees'
                                          )
    expected_employees = fields.Integer(string='Expected Employees', default=1,
                                        help="Number of extra new employees to be expected via the recruitment request.",
                                        tracking=True,
                                        index=True,
                                        readonly=True, states={'draft':[('readonly', False)]}
                                        )
    date_expected = fields.Date(string='Date Expected',
                                tracking=True,
                                default=fields.Date.context_today, index=True,
                                readonly=True, states={'draft':[('readonly', False)]}
                                )
    requirements = fields.Text('Job Requirements',
                               help="Please specify your requirements on new employees",
                               states={'done':[('readonly', True)]},
                               )
    description_job = fields.Text(string='Job Description',
                                help='Please describe the job',
                                states={'done':[('readonly', True)]},
                                )
    applicant_ids = fields.One2many('hr.applicant', 'approval_id', string='Applicants', readonly=True, index=True)
    employee_ids = fields.One2many('hr.employee', 'approval_id', string='Recruited Employees', compute='_compute_recruited_employees', store=True, index=True)

    employees_count = fields.Integer('# of Employees', compute='_compute_count_recruited_employees', store=True, index=True)
    recruited_employees = fields.Float('Recruited Employees Rate', compute='_compute_recruited_employee_percentage')
    applicants_count = fields.Integer('# of Applications', compute='_compute_count_applicants', store=True, index=True)

    job_state = fields.Selection(string='Job Status', related='job_id.state', store=True)

    more_than_expected = fields.Boolean(string='More than expected', compute='_compute_more_than_expected',
                                        store=True, index=True)

    _sql_constraints = [
        ('expected_employees_check',
         'CHECK(expected_employees > 0)',
         "Expected Employees must be greater than 0"),
    ]

    @api.depends('employee_id')
    def _compute_can_change_demand_dept(self):
        for r in self:
            if r.env.user.user_has_groups('hr_recruitment.group_hr_recruitment_user'):
                r.can_change_demand_dept = True
            else:
                r.can_change_demand_dept = False

    @api.depends('applicant_ids', 'applicant_ids.emp_id')
    def _compute_recruited_employees(self):
        for r in self:
            applicants_hired = r.applicant_ids.filtered(lambda app: app.emp_id != False)
            if applicants_hired:
                r.employee_ids = applicants_hired.mapped('emp_id')
            else:
                r.employee_ids = False

    @api.depends('expected_employees', 'employees_count')
    def _compute_more_than_expected(self):
        for r in self:
            if r.expected_employees < r.employees_count:
                r.more_than_expected = True
            else:
                r.more_than_expected = False

    @api.depends('job_id', 'demand_department_id')
    def _compute_count_dept_employees(self):
        for r in self:
            employees = 0
            if r.job_id and r.demand_department_id:
                domain = [('department_id', '=', r.demand_department_id.id), ('job_id', '=', r.job_id.id)]
            elif not r.job_id and r.demand_department_id:
                domain = [('department_id', '=', r.demand_department_id.id)]
            elif self.job_id and not self.demand_department_id:
                domain = [('job_id', '=', r.job_id.id)]
            else:
                domain = []

            if domain:
                employee_ids = self.env['hr.employee'].search(domain)
                employees = len(employee_ids)

            r.no_of_hired_employee = employees

    @api.onchange('job_id')
    def _onchange_job_id(self):
        if self.job_id:
            if self.job_id.description and not self.description_job:
                self.description_job = self.job_id.description
            if self.job_id.requirements and not self.requirements:
                self.requirements = self.job_id.requirements

    @api.depends('employee_ids')
    def _compute_count_recruited_employees(self):
        for r in self:
            r.employees_count = len(r.employee_ids)

    @api.depends('employees_count')
    def _compute_recruited_employee_percentage(self):
        for r in self:
            if r.expected_employees > 0:
                r.recruited_employees = 100.0 * r.employees_count / r.expected_employees
            else:
                r.recruited_employees = 0

    @api.depends('applicant_ids')
    def _compute_count_applicants(self):
        for r in self:
            r.applicants_count = len(r.applicant_ids)

    def _prepare_new_job_data(self):
        self.ensure_one()
        return {
            'name': self.job_tmp,
            'expected_employees': self.expected_employees,
            'department_id': self.demand_department_id.id,
            'company_id': self.company_id.id,
            'description': self.description,
            'requirements': self.requirements,
            'user_id': self.employee_id.user_id.id,
            }

    def action_validate(self):
        res = super(ApprovalRequest, self).action_validate()
        HRJob = self.env['hr.job']
        for r in self.filtered(lambda r: r.type == 'recruitment' and r.state == 'validate'):
            if r.job_id:
                job = r.job_id
            elif r.job_tmp:
                job = HRJob.create(r._prepare_new_job_data())
            else:
                raise ValidationError(_("Please select an existing job or contact your administrator for further help."))

            r.sudo().job_id = job
            job._suggest_no_of_recruitment()
        return res

    @api.constrains('job_id', 'state')
    def _check_existing_request(self):
        RequestSudo = self.env['approval.request'].sudo()
        for r in self:
            if r.job_id and r.state != 'done':
                request = RequestSudo.search([('id', '!=', r.id), ('state', '!=', 'done'), ('job_id', '=', r.job_id.id)], limit=1)
                if request:
                    raise ValidationError(_("An existing request for this job position already exists"))
