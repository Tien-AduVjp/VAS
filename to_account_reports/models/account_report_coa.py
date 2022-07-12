# -*- coding: utf-8 -*-

from odoo import models, api, _
from datetime import datetime


class ReportAccountCoa(models.AbstractModel):
    _name = "account.coa.report"
    _description = "Chart of Account Report"
    _inherit = "account.general.ledger"

    filter_date = {'date_from': '', 'date_to': '', 'filter': 'this_month'}
    filter_comparison = {'date_from': '', 'date_to': '', 'filter': 'no_comparison', 'number_period': 1}
    filter_cash_basis = False
    filter_all_entries = False
    filter_hierarchy = False
    filter_unfold_all = None

    def get_templates(self):
        templates = super(ReportAccountCoa, self).get_templates()
        templates['main_template'] = 'to_account_reports.template_coa_report'
        return templates

    def get_columns_name(self, options):
        columns = [
            {'name': ''},
            {'name': '', 'class': 'number'},
            {'name': _('Debit'), 'class': 'number'},
            {'name': _('Credit'), 'class': 'number'},
        ]
        if options.get('comparison') and options['comparison'].get('periods'):
            columns += [
                {'name': _('Debit'), 'class': 'number'},
                {'name': _('Credit'), 'class': 'number'},
            ] * len(options['comparison']['periods'])
        return columns + [
            {'name': _('Debit'), 'class': 'number'},
            {'name': _('Credit'), 'class': 'number'},
            {'name': _('Debit'), 'class': 'number'},
            {'name': _('Credit'), 'class': 'number'},
        ]

    def _get_super_columns(self, options):
        date_cols = options.get('date') and [options['date']] or []
        date_cols += (options.get('comparison') or {}).get('periods', [])
        columns = [{'string': _('Code')}]
        columns += [{'string': _('Name')}]
        columns += [{'string': _('Initial Balance')}]
        columns += reversed(date_cols)
        columns += [{'string': _('Total')}]

        return {'columns': columns, 'x_offset': 0, 'merge': 2}

    def _post_process(self, grouped_accounts, initial_balances, options, comparison_table):
        lines = []
        context = self.env.context
        company_id = context.get('company_id') or self.env.company
        title_index = ''
        sorted_accounts = sorted(grouped_accounts, key=lambda a: a.code)
        zero_value = ''
        sum_columns = [0, 0, 0, 0]
        for period in range(len(comparison_table)):
            sum_columns += [0, 0]
        for account in sorted_accounts:
            if not account.show_both_dr_and_cr_trial_balance:
                # skip accounts with all periods = 0 and no initial balance
                non_zero = False
                for p in range(len(comparison_table)):
                    if (grouped_accounts[account][p]['debit'] or grouped_accounts[account][p]['credit']) or\
                        not company_id.currency_id.is_zero(initial_balances.get(account, 0)):
                        non_zero = True
                if not non_zero:
                    continue

                initial_balance = initial_balances.get(account, 0.0)
                sum_columns[0] += initial_balance if initial_balance > 0 else 0
                sum_columns[1] += -initial_balance if initial_balance < 0 else 0
                cols = [
                    {'name': initial_balance > 0 and self.format_value(initial_balance) or zero_value, 'no_format_name': initial_balance > 0 and initial_balance or 0},
                    {'name': initial_balance < 0 and self.format_value(-initial_balance) or zero_value, 'no_format_name': initial_balance < 0 and abs(initial_balance) or 0},
                ]
            else:
                initial_balance = initial_balances.get(account, [])
                initial_debit = sum([initial_balance[k] if initial_balance[k] > 0 else 0 for k in initial_balance])
                initial_credit = sum([initial_balance[k] if initial_balance[k] < 0 else 0 for k in initial_balance])
                sum_columns[0] += initial_debit
                sum_columns[1] += abs(initial_credit)
                cols = [
                    {'name': initial_debit > 0 and self.format_value(initial_debit) or zero_value, 'no_format_name': initial_debit},
                    {'name': initial_credit < 0 and self.format_value(abs(initial_credit)) or zero_value, 'no_format_name': abs(initial_credit)},
                ]
            total_periods = 0
            for period in range(len(comparison_table)):
                if account.show_both_dr_and_cr_trial_balance:
                    amount = sum([grouped_accounts[account][k][period]['balance'] for k in grouped_accounts[account]])
                    debit = sum([grouped_accounts[account][k][period]['debit'] for k in grouped_accounts[account]])
                    credit = sum([grouped_accounts[account][k][period]['credit'] for k in grouped_accounts[account]])
                else:
                    amount = grouped_accounts[account][period]['balance']
                    debit = grouped_accounts[account][period]['debit']
                    credit = grouped_accounts[account][period]['credit']
                total_periods += amount
                cols += [{'name': debit > 0 and self.format_value(debit) or zero_value, 'no_format_name': debit > 0 and debit or 0},
                         {'name': credit > 0 and self.format_value(credit) or zero_value, 'no_format_name': credit > 0 and abs(credit) or 0}]
                # In sum_columns, the first 2 elements are the initial balance's Debit and Credit
                # index of the credit of previous column generally is:
                p_indice = period * 2 + 1
                sum_columns[(p_indice) + 1] += debit if debit > 0 else 0
                sum_columns[(p_indice) + 2] += credit if credit > 0 else 0

            if account.show_both_dr_and_cr_trial_balance:
                total_debit = 0
                total_credit = 0
                for partner in grouped_accounts[account]:
                    total_per_partner = (initial_balances[account][partner] if ((initial_balances and initial_balances[account]) and partner in initial_balances[account]) else 0) + sum(grouped_accounts[account][partner][period]['balance'] for period in range(len(comparison_table)))
                    if total_per_partner > 0:
                        total_debit += total_per_partner
                    else:
                        total_credit += total_per_partner
                sum_columns[-2] += total_debit
                sum_columns[-1] += abs(total_credit)
                cols += [
                    {'name': total_debit > 0 and self.format_value(total_debit) or zero_value, 'no_format_name': total_debit},
                    {'name': total_credit < 0 and self.format_value(abs(total_credit)) or zero_value, 'no_format_name': abs(total_credit)},
                    ]
            else:
                total_amount = initial_balance + total_periods
                sum_columns[-2] += total_amount if total_amount > 0 else 0
                sum_columns[-1] += -total_amount if total_amount < 0 else 0
                cols += [
                    {'name': total_amount > 0 and self.format_value(total_amount) or zero_value, 'no_format_name': total_amount > 0 and total_amount or 0},
                    {'name': total_amount < 0 and self.format_value(-total_amount) or zero_value, 'no_format_name': total_amount < 0 and abs(total_amount) or 0},
                    ]
            lines.append({
                'id': account.id,
                'code': account.code,
                'name': account.name,
                'columns': cols,
                'unfoldable': False,
                'caret_options': 'account.account',
                'is_coa_report': True,
            })
        lines.append({
             'id': 'grouped_accounts_total',
             'name': _('Total'),
             'colspan': 2,
             'class': 'o_af_reports_domain_total',
             'columns': [{'name': self.format_value(v)} for v in sum_columns],
             'level': 0,
        })
        return lines

    @api.model
    def get_lines(self, options, line_id=None):
        context = self.env.context
        company_id = context.get('company_id') or self.env.company
        grouped_accounts = {}
        initial_balances = {}
        comparison_table = [options.get('date')]
        comparison_table += options.get('comparison') and options['comparison'].get('periods') or []

        # get the balance of accounts for each period
        period_number = 0
        for period in reversed(comparison_table):
            res = self.with_context(date_from_aml=period['date_from'], date_to=period['date_to'], date_from=period['date_from'] and company_id.compute_fiscalyear_dates(datetime.strptime(period['date_from'], "%Y-%m-%d"))['date_from'] or None).group_by_account_id(options, line_id)  # Aml go back to the beginning of the user chosen range but the amount on the account line should go back to either the beginning of the fy or the beginning of times depending on the account
            if period_number == 0:
                initial_balances = dict([(k, res[k]['initial_bal']['balance']) for k in res])
            for account in res:
                if account.show_both_dr_and_cr_trial_balance:
                    res_account = self.with_context(date_from_aml=period['date_from'], date_to=period['date_to'], date_from=period['date_from'] and company_id.compute_fiscalyear_dates(datetime.strptime(period['date_from'], "%Y-%m-%d"))['date_from'] or None).group_by_account_id(options, line_id=account.id, group_by_partner=True)
                    if period_number == 0:
                        initial_balances[account] = dict([(k,res_account[k]['initial_bal']['balance']) for k in res_account])
                    if account not in grouped_accounts:
                        grouped_accounts[account] = {}
                    for partner in res_account:
                        if partner not in grouped_accounts[account]:
                            grouped_accounts[account][partner] = [{'balance': 0, 'debit': 0, 'credit': 0} for p in comparison_table]
                        grouped_accounts[account][partner][period_number]['balance'] = res_account[partner]['balance'] - res_account[partner]['initial_bal']['balance']
                        grouped_accounts[account][partner][period_number]['debit'] = res_account[partner]['debit'] - res_account[partner]['initial_bal']['debit']
                        grouped_accounts[account][partner][period_number]['credit'] = res_account[partner]['credit'] - res_account[partner]['initial_bal']['credit']
                else:
                    if account not in grouped_accounts:
                        grouped_accounts[account] = [{'balance': 0, 'debit': 0, 'credit': 0} for p in comparison_table]
                    grouped_accounts[account][period_number]['balance'] = res[account]['balance'] - res[account]['initial_bal']['balance']
                    grouped_accounts[account][period_number]['debit'] = res[account]['debit'] - res[account]['initial_bal']['debit']
                    grouped_accounts[account][period_number]['credit'] = res[account]['credit'] - res[account]['initial_bal']['credit']
            period_number += 1
        # build the report
        lines = self._post_process(grouped_accounts, initial_balances, options, comparison_table)
        return lines

    @api.model
    def get_report_name(self):
        return _("Trial Balance")
    
    def get_template_ref(self):
        return ''
