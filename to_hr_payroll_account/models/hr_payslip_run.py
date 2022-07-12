from odoo import fields, models, _
from odoo.exceptions import UserError


class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'

    def _get_default_journal_id(self):
        company_id = self.env.company.id
        return self.env['account.journal'].search([
            ('code', '=', 'SAL'),
            ('company_id', '=', company_id)
            ], limit=1)

    journal_id = fields.Many2one('account.journal', 'Salary Journal', states={'draft': [('readonly', False)]}, readonly=True,
        required=True, default=_get_default_journal_id, tracking=True)
    move_id = fields.Many2one('account.move', string='Journal Entry', help="The journal entry for all payslips of this batch.")
    moves_count = fields.Integer(string='Journal Entries Count', compute='_compute_moves_count')
    date = fields.Date('Accounting Date', states={'draft': [('readonly', False)]}, readonly=True,
        help="Keep empty to use the period of the validation (Payslip Batch) end date.")

    def _get_accounting_date(self):
        self.ensure_one()
        return self.date or self.date_end or fields.Date.today()

    def _prepare_account_move_lines_data(self):
        self.ensure_one()
        date = self._get_accounting_date()
        vals_list = []
        currency = self.currency_id

        # save the sum of credit and debit for adjustment later if they are not equal
        debit_sum = 0.0
        credit_sum = 0.0

        self.slip_ids._compute_details_by_salary_rule_category()
        for rule in self.mapped('slip_ids.details_by_salary_rule_category.salary_rule_id').filtered(lambda r: r.generate_account_move_line):
            # group payslip lines by analytic account
            account_group = {}
            debit_partner = rule._get_partner(credit_account=False)
            credit_partner = rule._get_partner(credit_account=True)
            for line in self.slip_ids.details_by_salary_rule_category.filtered(lambda l: l.salary_rule_id == rule):
                dict_hash = line._get_group_hashcode()
                account_group.setdefault(dict_hash, line)
                account_group[dict_hash] |= line

            # iterate over the group and generate journal item for each
            for __, payslip_lines in account_group.items():
                # override debit and credit partners if rule requires employee as partner
                if rule.employee_journal_item:
                    debit_partner = payslip_lines[0]._get_partner(credit_account=False)
                    credit_partner = payslip_lines[0]._get_partner(credit_account=True)
                accounts = payslip_lines[0]._get_accounts()
                debit_account = accounts['debit_account']
                credit_account = accounts['credit_account']
                analytic_account = accounts['analytic_account']
                analytic_tags = accounts['analytic_tags']
                amount = 0.0
                for line in payslip_lines:
                    amount += currency.round(line.slip_id.credit_note and -line.total or line.total)
                if currency.is_zero(amount):
                    continue

                if debit_account:
                    debit_line = {
                        'name': rule.name,
                        'partner_id': debit_partner and debit_partner.id or False,
                        'account_id': debit_account.id,
                        'journal_id': self.journal_id.id,
                        'date': date,
                        'debit': amount > 0.0 and amount or 0.0,
                        'credit': amount < 0.0 and -amount or 0.0,
                        'analytic_account_id': analytic_account.id if analytic_account and rule.anylytic_option == 'debit_account' else False,
                        'analytic_tag_ids': [(6, 0, analytic_tags.ids)] if rule.anylytic_option == 'debit_account' else [(6, 0, [])],
                        'tax_line_id': rule.account_tax_id and rule.account_tax_id.id or False,
                        'salary_rule_id': rule.id,
                    }
                    vals_list.append(debit_line)
                    debit_sum += debit_line['debit'] - debit_line['credit']

                if credit_account:
                    credit_line = {
                        'name': rule.name,
                        'partner_id': credit_partner and credit_partner.id or False,
                        'account_id': credit_account.id,
                        'journal_id': self.journal_id.id,
                        'date': date,
                        'debit': amount < 0.0 and -amount or 0.0,
                        'credit': amount > 0.0 and amount or 0.0,
                        'analytic_account_id': analytic_account.id if analytic_account and rule.anylytic_option == 'credit_account' else False,
                        'analytic_tag_ids': [(6, 0, analytic_tags.ids)] if rule.anylytic_option == 'credit_account' else [(6, 0, [])],
                        'tax_line_id': rule.account_tax_id.id,
                        'salary_rule_id': rule.id,
                    }
                    vals_list.append(credit_line)
                    credit_sum += credit_line['credit'] - credit_line['debit']

        # generate adjustment line
        if currency.compare_amounts(credit_sum, debit_sum) == -1:
            account = self.company_id.general_employee_payable_account_id
            if not account:
                raise UserError(_("Payable account was not configured for the company '%s'. Please do it in Accounting/Payroll Settings") % self.company_id.name)
            adjust_credit = {
                'name': _('Adjustment Entry'),
                'partner_id': False,
                'account_id': account.id,
                'journal_id': self.journal_id.id,
                'date': date,
                'debit': 0.0,
                'credit': currency.round(debit_sum - credit_sum),
            }
            vals_list.append(adjust_credit)

        elif currency.compare_amounts(debit_sum, credit_sum) == -1:
            account = self.company_id.general_employee_payable_account_id
            if not account:
                raise UserError(_("Payable account was not configured for the company '%s'. Please do it in Accounting/Payroll Settings") % self.company_id.name)
            adjust_debit = {
                'name': _('Adjustment Entry'),
                'partner_id': False,
                'account_id': account.id,
                'journal_id': self.journal_id.id,
                'date': date,
                'debit': currency.round(credit_sum - debit_sum),
                'credit': 0.0,
            }
            vals_list.append(adjust_debit)
        return vals_list

    def _prepare_account_move_data(self):
        self.ensure_one()
        date = self._get_accounting_date()
        return {
            'narration': self.name,
            'ref': self.name,
            'journal_id': self.journal_id.id,
            'date': date,
            'line_ids': [(0, 0, vals) for vals in self._prepare_account_move_lines_data()],
            'auto_post': True if date > fields.Date.today() else False,
            }

    def _generate_account_move(self):
        for r in self:
            move = self.env['account.move'].sudo().create(r._prepare_account_move_data())
            r.slip_ids.write({'move_id': move.id})

    def action_verify_payslips(self):
        batches_with_account_move = self.filtered(lambda r: r.company_id.payslip_batch_journal_entry)

        # process payslip batches with account moves generation
        if batches_with_account_move:
            batches_with_account_move._generate_account_move()
            super(HrPayslipRun, batches_with_account_move.with_context(ignore_payslip_account_move_generation=True)).action_verify_payslips()

        # process the remaining payslip batches
        remaining = self - batches_with_account_move
        if remaining:
            super(HrPayslipRun, remaining).action_verify_payslips()

    def _compute_moves_count(self):
        # read group, by pass ORM to avoid access right error
        self.env.cr.execute("""
        SELECT r.id AS payslip_run_id, COUNT(distinct(m.id)) as move_count
        FROM account_move AS m
        JOIN hr_payslip AS ps ON ps.move_id = m.id
        JOIN hr_payslip_run AS r ON r.id = ps.payslip_run_id
        WHERE r.id in %s
        GROUP BY r.id
        """, (tuple(self.ids),))
        moves_data = self.env.cr.dictfetchall()
        mapped_data = dict([(dict_data['payslip_run_id'], dict_data['move_count']) for dict_data in moves_data])
        for r in self:
            r.moves_count = mapped_data.get(r.id, 0)

    def action_view_account_moves(self):
        moves = self.mapped('slip_ids.move_id')
        action = self.env['ir.actions.act_window']._for_xml_id('account.action_move_journal_line')
        action['context'] = {}
        action['domain'] = "[('id', 'in', %s)]" % str(moves.ids)
        return action
