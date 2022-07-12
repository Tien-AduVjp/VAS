from odoo import models, fields, api


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # 'employee' is a field of 'base' module but does not display on any view or use in anywhere,
    # so I make use for it here
    employee = fields.Boolean(compute='_compute_is_employee', search='_search_is_employee',
                              compute_sudo=True, groups='hr.group_hr_user')
    employee_ids = fields.Many2many('hr.employee', 'viin_res_partner_employee_rel', 'partner_id', 'employee_id',
                                    string='Related Employees', compute='_compute_employee_ids', store=True,
                                    groups="hr.group_hr_user")
    hr_applicant_ids = fields.One2many('hr.applicant', 'partner_id', string='Applicants',
                                       groups='hr_recruitment.group_hr_recruitment_user',
                                       help="The HR applicants of this partner")
    hr_applicants_count = fields.Integer(string='Applicants Count', compute='_compute_hr_applicants_count',
                                         groups='hr_recruitment.group_hr_recruitment_user')

    @api.depends('user_ids.employee_ids')
    def _compute_employee_ids(self):
        for r in self:
            r.employee_ids = r.user_ids.mapped('employee_ids')

    def _compute_is_employee(self):
        employees = self.env['hr.employee'].search([])
        for r in self:
            r.employee = bool(employees.filtered(lambda emp: emp.address_home_id == r) | r.user_ids.mapped('employee_ids'))

    def _search_is_employee(self, operator, value):
        employees = self.env['hr.employee'].search([])
        if operator == '=' and value or operator == '!=' and not value:
            new_operator = 'in'
        elif operator == '=' and not value or operator == '!=' and value:
            new_operator = 'not in'
        else:
            return []
        return [
            ('id', new_operator, (employees.user_id.partner_id | employees.address_home_id).ids),
        ]

    def _compute_hr_applicants_count(self):
        data = self.env['hr.applicant'].read_group([('partner_id', 'in', self.ids)], ['partner_id'], ['partner_id'])
        mapped_data = dict([(dict_data['partner_id'][0], dict_data['partner_id_count']) for dict_data in data])
        for r in self:
            r.hr_applicants_count = mapped_data.get(r.id, 0)

    def action_view_applicants(self):
        applicants = self.env['hr.applicant'].search([('partner_id', '=', self.ids)])

        action = self.env.ref('hr_recruitment.crm_case_categ0_act_job')
        result = action.read()[0]

        # choose the view_mode accordingly
        if len(applicants) != 1:
            result['domain'] = "[('partner_id', 'in', " + str(self.ids) + ")]"
        elif len(applicants) == 1:
            res = self.env.ref('hr_recruitment.crm_case_form_view_job', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = applicants.id
        return result

    def _get_hr_allowed_fields(self):
        return self._address_fields() + ['phone', 'mobile', 'email', 'dob', 'bank_ids', 'name', 'company_id', 'type']

    def write(self, vals):
        """
        Dirty hack to allow HR officer to update employee's private address without res.users access rights error
        """
        if self.env.user.has_group('hr.group_hr_user') and all(f in self._get_hr_allowed_fields() for f in vals.keys()):
            self = self.with_context(group_hr_user_update_private_address=True)
        return super(ResPartner, self).write(vals)
