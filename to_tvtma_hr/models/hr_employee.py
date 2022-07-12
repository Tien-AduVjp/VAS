from odoo import models, fields


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    vat = fields.Char(string='Personal Tax Code', related='address_home_id.vat', store=True, readonly=False, groups="hr.group_hr_user",
                      help="The tax identification number that is related to the corresponding partner record specified in the field Private Address")
    hr_applicant_ids = fields.One2many('hr.applicant', 'emp_id', string='Applicants', groups='hr_recruitment.group_hr_recruitment_user',
                                       help="The HR applicants that link to this employee")
    hr_applicants_count = fields.Integer(string='Applicants Count', compute='_compute_hr_applicants_count',
                                         groups='hr_recruitment.group_hr_recruitment_user')
    
    def _compute_hr_applicants_count(self):
        data = self.env['hr.applicant'].read_group([('emp_id', 'in', self.ids)], ['emp_id'], ['emp_id'])
        mapped_data = dict([(dict_data['emp_id'][0], dict_data['emp_id_count']) for dict_data in data])
        for r in self:
            r.hr_applicants_count = mapped_data.get(r.id, 0)

    def action_view_applicants(self):
        applicants = self.env['hr.applicant'].search([('emp_id', '=', self.ids)])

        action = self.env.ref('hr_recruitment.crm_case_categ0_act_job')
        result = action.read()[0]

        # choose the view_mode accordingly
        if len(applicants) != 1:
            result['domain'] = "[('emp_id', 'in', %s)]" % str(self.ids)
        elif len(applicants) == 1:
            res = self.env.ref('hr_recruitment.crm_case_form_view_job', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = applicants.id
        return result
