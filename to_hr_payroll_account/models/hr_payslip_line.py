from odoo import models, _
from odoo.exceptions import ValidationError, UserError


class HrPayslipLine(models.Model):
    _inherit = 'hr.payslip.line'

    def _get_partner(self, credit_account):
        """
        Get partner of the slip line to use in account move line
        """
        return self.salary_rule_id._get_partner(credit_account, self.slip_id.employee_id)

    def _get_accounts(self):
        self.ensure_one()
        # use sudo to avoid access error when analytic accounting is not enabled
        self_sudo = self.sudo()
        contract_accounts = self_sudo.contract_id._get_accounts()
        return {
            'debit_account': self_sudo.salary_rule_id.account_debit or contract_accounts['expense_account'] if self_sudo.salary_rule_id.generate_account_move_line else self_sudo.env['account.account'],
            'credit_account': self_sudo.salary_rule_id.account_credit if self_sudo.salary_rule_id.generate_account_move_line else self_sudo.env['account.account'],
            'analytic_account': self_sudo.salary_rule_id.analytic_account_id or contract_accounts['analytic_account'] if self_sudo.salary_rule_id.generate_account_move_line and self_sudo.salary_rule_id.anylytic_option != 'none' else self_sudo.env['account.analytic.account'],
            'analytic_tags': self_sudo.salary_rule_id.analytic_tag_ids or contract_accounts['analytic_tags'] if self_sudo.salary_rule_id.generate_account_move_line and self_sudo.salary_rule_id.anylytic_option != 'none' else self_sudo.env['account.analytic.tag'],
            }

    def _get_group_hashcode(self):
        self.ensure_one()
        d = self._get_accounts()
        d.update({
            'debit_account': d.get('debit_account').id or 'False',
            'credit_account': d.get('credit_account').id or 'False',
            'analytic_account': d.get('analytic_account').id or 'False',
            'analytic_tags': d.get('analytic_tags').ids or 'False',
            'register_partner': self.salary_rule_id.register_id.partner_id.id  or 'False',
            'generate_account_move_line': 'True' if self.salary_rule_id.generate_account_move_line else 'False',
            'anylytic_option': self.salary_rule_id.anylytic_option,
            'employee_id': self.slip_id.employee_id.id if self.salary_rule_id.generate_account_move_line and self.salary_rule_id.employee_journal_item else 'False'
            })
        hashcode = []
        for k, v in d.items():
            hashcode.append('%s:%s' % (k, v))
        hashcode = '-'.join(hashcode)
        return hashcode

    def _prepare_account_move_lines_data(self):
        slip = self.mapped('slip_id')
        if len(slip) > 1:
            raise ValidationError(_("Could not prepare journal items data for multiple payslip at the same time. This could be a programming error!"))

        currency = slip.currency_id or self.env.company.currency_id
        date = slip.date or slip.date_to
        vals_list = []
        debit_sum = 0.0
        credit_sum = 0.0
        for line in self.filtered(lambda l: l.salary_rule_id.generate_account_move_line):
            amount = currency.round(slip.credit_note and -line.total or line.total)
            if currency.is_zero(amount):
                continue

            accounts = line._get_accounts()

            debit_account_id = accounts['debit_account'].id
            credit_account_id = accounts['credit_account'].id
            analytic_account = accounts['analytic_account']
            analytic_tags = accounts['analytic_tags']

            if debit_account_id:
                partner = line._get_partner(credit_account=False)
                debit_line = {
                    'name': line.name,
                    'partner_id': partner and partner.id or False,
                    'account_id': debit_account_id,
                    'journal_id': slip.journal_id.id,
                    'date': date,
                    'debit': amount > 0.0 and amount or 0.0,
                    'credit': amount < 0.0 and -amount or 0.0,
                    'analytic_account_id': analytic_account.id if analytic_account and line.salary_rule_id.anylytic_option == 'debit_account' else False,
                    'analytic_tag_ids': [(6, 0, analytic_tags.ids)] if line.salary_rule_id.anylytic_option == 'debit_account' else [(6, 0, [])],
                    'tax_line_id': line.salary_rule_id.account_tax_id.id,
                    'salary_rule_id': line.salary_rule_id.id,
                }
                vals_list.append(debit_line)
                debit_sum += debit_line['debit'] - debit_line['credit']

            if credit_account_id:
                partner = line._get_partner(credit_account=True)
                credit_line = {
                    'name': line.name,
                    'partner_id': partner and partner.id or False,
                    'account_id': credit_account_id,
                    'journal_id': slip.journal_id.id,
                    'date': date,
                    'debit': amount < 0.0 and -amount or 0.0,
                    'credit': amount > 0.0 and amount or 0.0,
                    'analytic_account_id': analytic_account.id if analytic_account and line.salary_rule_id.anylytic_option == 'credit_account' else False,
                    'analytic_tag_ids': [(6, 0, analytic_tags.ids)] if line.salary_rule_id.anylytic_option == 'credit_account' else [(6, 0, [])],
                    'tax_line_id': line.salary_rule_id.account_tax_id.id,
                    'salary_rule_id': line.salary_rule_id.id,
                }
                vals_list.append(credit_line)
                credit_sum += credit_line['credit'] - credit_line['debit']

        if currency.compare_amounts(credit_sum, debit_sum) == -1:
            account = slip.employee_id._get_payable_account()
            if not account:
                raise UserError(_("Payable Account was not configured for neither the employee '%s' nor its related company."
                    " Please make sure a payable account is specified in Payroll/Accounting Settings and/or the private address of the employee.")
                    % slip.employee_id.name
                    )
            adjust_credit = {
                'name': _('Adjustment Entry'),
                'partner_id': False,
                'account_id': account.id,
                'journal_id': slip.journal_id.id,
                'date': date,
                'debit': 0.0,
                'credit': currency.round(debit_sum - credit_sum),
            }
            vals_list.append(adjust_credit)

        elif currency.compare_amounts(debit_sum, credit_sum) == -1:
            account = account = slip.employee_id._get_payable_account()
            if not account:
                raise UserError(_("Payable Account was not configured for neither the employee '%s' nor its related company."
                    " Please make sure a payable account is specified in Payroll/Accounting Settings and/or the private address of the employee.")
                    % slip.employee_id.name
                    )
            adjust_debit = {
                'name': _('Adjustment Entry'),
                'partner_id': False,
                'account_id': account.id,
                'journal_id': slip.journal_id.id,
                'date': date,
                'debit': currency.round(credit_sum - debit_sum),
                'credit': 0.0,
            }
            vals_list.append(adjust_debit)
        return vals_list
