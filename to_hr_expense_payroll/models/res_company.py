from odoo import models, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    def _prepare_contribution_register_data(self):
        """
        This will be called by the `_generate_contribution_register()`
        """
        res = super(ResCompany, self)._prepare_contribution_register_data()
        res.append({
            'name': _('HR Expense Reimbursement'),
            'partner_id': False,
            'category_id': self.env.ref('to_hr_expense_payroll.hr_contribution_category_reimbursement').id,
            'company_id': self.id
            })
        return res

    def _prepare_salary_rule_categories_data(self):
        res = super(ResCompany, self)._prepare_salary_rule_categories_data()
        res.append({
            'name': _('HR Expense Reimbursement'),
            'code': 'EXREIMB',
            'company_id': self.id
            })
        return res

    def _parepare_salary_rules_vals_list(self, struct):
        vals_list = super(ResCompany, self)._parepare_salary_rules_vals_list(struct)
        for r in self:
            vals_list.append(r._prepare_expense_salary_rules(struct))
            for vals in vals_list:
                if vals.get('code') == 'NET' and vals.get('company_id') == r.id:
                    vals['amount_python_compute'] += ' + categories.EXREIMB'
        return vals_list

    def _prepare_expense_salary_rules(self, struct):
        self.ensure_one()
        return {
            'name': _('HR Expense Reimbursement Amount'),
            'sequence': 170,
            'code': 'EXREIMB',
            'struct_id': struct.id,
            'category_id': self._get_salary_rule_categ('EXREIMB').id,
            'condition_select': 'python',
            'condition_python': 'result = True if payslip.hr_expense_ids else False',
            'amount_select': 'code',
            'appears_on_payslip': True,
            'amount_python_compute': "result = sum(payslip.hr_expense_ids.mapped('total_amount'))",
            'register_id': self._get_contribution_register(_("HR Expense Reimbursement")).id,
            'company_id': self.id
            }

    def _generate_expense_salary_rules(self):
        self._generate_contribution_register()
        self._generate_salary_rule_categories()

        salary_rule_obj = self.env['hr.salary.rule'].sudo()
        structure_obj = self.env['hr.payroll.structure'].sudo()

        structs = structure_obj.search([
            ('company_id', 'in', self.ids),
            ('code', '=', 'BASE')
            ])
        existing_rules = self.env['hr.salary.rule'].sudo().search([
            ('struct_id', 'in', structs.ids),
            ('company_id', 'in', self.ids),
            ('code', '=', 'EXREIMB')
            ])
        vals_list = []
        for r in self:
            for struct in structs.filtered(lambda s: s.company_id == r):
                if not existing_rules.filtered(lambda rule: rule.struct_id == struct and rule.company_id == r):
                    vals_list.append(r._prepare_expense_salary_rules(struct))
        if vals_list:
            return salary_rule_obj.create(vals_list)
        return self.env['hr.salary.rule']

    def _add_hr_expense_to_net_rule(self):
        """
        include HR Expense in Net rules for HR expense reimbursement
        """
        net_rules = self._get_salary_rules_by_code('NET')
        for rule in net_rules.filtered(lambda r: 'categories.EXREIMB' not in r.amount_python_compute):
            rule.write({
                'amount_python_compute': '%s%s' % (rule.amount_python_compute, ' + categories.EXREIMB')
                })
