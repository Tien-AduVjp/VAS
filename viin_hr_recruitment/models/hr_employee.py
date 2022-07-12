from odoo import models, fields


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    hr_applicants_count = fields.Integer(string='Applicants Count', compute='_compute_hr_applicants_count',
                                         groups='hr_recruitment.group_hr_recruitment_user')

    def _compute_hr_applicants_count(self):
        data = self.env['hr.applicant'].read_group([('emp_id', 'in', self.ids)], ['emp_id'], ['emp_id'])
        mapped_data = dict([(dict_data['emp_id'][0], dict_data['emp_id_count']) for dict_data in data])
        for r in self:
            r.hr_applicants_count = mapped_data.get(r.id, 0)

    def action_view_applicants(self):

        result = self.env['ir.actions.act_window']._for_xml_id('hr_recruitment.crm_case_categ0_act_job')

        # choose the view_mode accordingly
        if self.hr_applicants_count != 1:
            result['domain'] = "[('emp_id', 'in', %s)]" % str(self.ids)
        elif self.hr_applicants_count == 1:
            res = self.env.ref('hr_recruitment.crm_case_form_view_job', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = self.applicant_id.id
        return result
