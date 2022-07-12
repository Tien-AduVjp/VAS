from odoo import models

VIETNAM_CONTRIB_DATA = {
    'SOCIAL_INSURANCE': {
        'employee_contrib_rate': 8.0,
        'company_contrib_rate': 17.5,
        'computation_method': 'max_unpaid_days',
        'max_unpaid_days': 14.0,
        },
    'HEALTH_INSURANCE': {
        'employee_contrib_rate': 1.5,
        'company_contrib_rate': 3.0,
        'computation_method': 'max_unpaid_days',
        'max_unpaid_days': 14.0,
        },
    'UNEMPLOYMENT_UNSURANCE': {
        'employee_contrib_rate': 1.0,
        'company_contrib_rate': 1.0,
        'computation_method': 'max_unpaid_days',
        'max_unpaid_days': 14.0,
        },
    'LABOR_UNION': {
        'employee_contrib_rate': 1.0,
        'company_contrib_rate': 2.0,
        'computation_method': 'max_unpaid_days',
        'max_unpaid_days': 14.0,
        }
    }


class ResCompany(models.Model):
    _inherit = 'res.company'

    def _prepare_payrol_contribution_types_data(self):
        contrib_type_vals_list = super(ResCompany, self)._prepare_payrol_contribution_types_data()
        if self.country_id == self.env.ref('base.vn'):
            for k, vals in VIETNAM_CONTRIB_DATA.items():
                for contrib_type_vals in contrib_type_vals_list:
                    if contrib_type_vals['code'] == k:
                        contrib_type_vals.update(vals)
        return contrib_type_vals_list

    def _set_payroll_contrib_data(self):
        vietnam = self.env.ref('base.vn')
        ContributionType = self.env['hr.payroll.contribution.type'].sudo()
        for company in self.filtered(lambda c: c.partner_id.country_id == vietnam):
            for k, vals in VIETNAM_CONTRIB_DATA.items():
                ContributionType.search([('company_id', '=', company.id), ('code', '=', k)]).write(vals)

            for reg in self.env['hr.payroll.contribution.register'].sudo().search([('state', '=', 'draft')]):
                reg.write({
                    'employee_contrib_rate': reg.type_id.employee_contrib_rate,
                    'company_contrib_rate': reg.type_id.company_contrib_rate,
                    'computation_method': reg.type_id.computation_method,
                    'max_unpaid_days': reg.type_id.max_unpaid_days,
                    })

    def _generate_vietnam_personal_tax_rules_data(self):
        vietnam = self.env.ref('base.vn')
        return [
            {
                'country_id': vietnam.id,
                'personal_tax_policy': 'escalation',
                'apply_tax_base_deduction': True,
                'personal_tax_base_ded': 11000000,
                'dependent_tax_base_ded': 4400000,
                'progress_ids': [
                    (0, 0, {
                        'base': 0,
                        'rate': 5.0,
                        }),
                    (0, 0, {
                        'base': 5000000,
                        'rate': 10.0,
                        }),
                    (0, 0, {
                        'base': 10000000,
                        'rate': 15.0,
                        }),
                    (0, 0, {
                        'base': 18000000,
                        'rate': 20.0,
                        }),
                    (0, 0, {
                        'base': 32000000,
                        'rate': 25.0,
                        }),
                    (0, 0, {
                        'base': 52000000,
                        'rate': 30.0,
                        }),
                    (0, 0, {
                        'base': 80000000,
                        'rate': 35.0,
                        }),
                    ]
                },
            {
                'country_id': vietnam.id,
                'personal_tax_policy': 'flat_rate',
                'apply_tax_base_deduction': False,
                'personal_tax_flat_rate': 10.0,
                },
            {
                'country_id': vietnam.id,
                'personal_tax_policy': 'flat_rate',
                'personal_tax_flat_rate': 20.0,
                'apply_tax_base_deduction': False,
                }
            ]

    def _parepare_salary_rules_vals_list(self, struct):
        """
        Override to includes PHONE into TBDED
        """
        vals_list = super(ResCompany, self)._parepare_salary_rules_vals_list(struct)
        for company in self.filtered(lambda c: c.country_id == self.env.ref('base.vn')):
            for vals in vals_list:
                if vals.get('code') == 'TBDED' and vals.get('company_id') == company.id:
                    vals['amount_python_compute'] += ' + categories.PHONE'
        return vals_list

    def _generate_personal_tax_rules(self):
        rules = self.env['personal.tax.rule'].create(self._generate_vietnam_personal_tax_rules_data())
        vietnam = self.env.ref('base.vn')
        vietnam_esc_rule = rules.filtered(lambda r: r.personal_tax_policy == 'escalation')
        self.env['hr.contract'].search([('employee_id.address_id.country_id', '=', vietnam.id), ('personal_tax_rule_id', '=', False)]).write({
            'personal_tax_rule_id': vietnam_esc_rule and vietnam_esc_rule[0].id or False
            })
        return rules

    def _generate_payroll_rules(self):
        res = super(ResCompany, self)._generate_payroll_rules()
        self._set_payroll_contrib_data()
        return res

    def write(self, vals):
        set_payroll_contrib_data = 'country_id' in vals
        res = super(ResCompany, self).write(vals)
        if set_payroll_contrib_data:
            self._set_payroll_contrib_data()
            self._add_phone_allowance_to_tax_base_deduction_vietnam()
        return res

    def _add_phone_allowance_to_tax_base_deduction_vietnam(self):
        """
        exclude phone allowance from tax base
        """
        companies = self.filtered(lambda c: c.partner_id.country_id == self.env.ref('base.vn'))
        personal_tax_base_deduction_rules = companies._get_salary_rules_by_code('TBDED')
        for rule in personal_tax_base_deduction_rules.filtered(lambda r: 'categories.PHONE' not in r.amount_python_compute):
            rule.write({
                'amount_python_compute': '%s%s' % (rule.amount_python_compute, ' + categories.PHONE')
                })
