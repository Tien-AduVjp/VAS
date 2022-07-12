from odoo import models, fields, _


class HRJob(models.Model):
    _inherit = 'hr.job'

    currency_id = fields.Many2one('res.currency', related="company_id.currency_id", store=True, tracking=True)

    wage = fields.Monetary('Basic Wage', help='The default basic wage for this job position', required=True, default=0.0, tracking=True)

    advantage_ids = fields.One2many('hr.job.advantage', 'job_id', string='Monthly Advantages', auto_join=True, groups='to_hr_payroll.group_hr_payroll_user')

    struct_id = fields.Many2one('hr.payroll.structure', string='Salary Structure', tracking=True, groups='to_hr_payroll.group_hr_payroll_user',
                                domain="['|', ('company_id','=',False), ('company_id','=',company_id)]",
                                help='The default salary structure that will be filled as default value for salary structure field on the HR contract document')

    resource_calendar_id = fields.Many2one('resource.calendar', string='Working Hours', tracking=True, help="Default working hours",
                                           domain="['|', ('company_id','=',False), ('company_id','=',company_id)]")

    def _prepare_salary_structure_data(self, company=None, parent=None):
        company = company or self.company_id
        return {
            'name': _('Salary structure for %s') % self.display_name,
            'code': self.env['to.base'].strip_accents(self.name.strip().replace(" ", "")).upper(),
            'company_id': company.id,
            'parent_id': parent and parent.id or False
            }

    def update_contract_advantages(self):
        for r in self:
            templates = r.advantage_ids.mapped('template_id')
            contracts = self.env['hr.contract'].search([('job_id', '=', r.id)])
            for contract in contracts:
                to_update = contract.advantage_ids.filtered(lambda adv: adv.template_id.id in templates.ids)
                to_del = contract.advantage_ids - to_update

                if to_del:
                    to_del.unlink()
                if to_update:
                    for adv in to_update:
                        job_adv = r.advantage_ids.filtered(lambda rec: rec.template_id.id == adv.template_id.id)
                        adv.write({
                            'job_advantage_id': job_adv[0].id,
                            'amount': job_adv[0].amount,
                            })

                new_to_add = r.advantage_ids.filtered(lambda adv: adv.template_id.id not in to_update.mapped('template_id').ids)

                vals_list = []
                for job_adv in new_to_add:
                    vals_list.append({
                        'job_advantage_id': job_adv.id,
                        'template_id': job_adv.template_id.id,
                        'contract_id': contract.id,
                        'amount': job_adv.amount,
                        'code': job_adv.code
                        })
                if vals_list:
                    self.env['hr.contract.advantage'].create(vals_list)

