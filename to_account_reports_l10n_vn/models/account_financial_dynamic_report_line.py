from odoo import models


class AccountFinanciaDynamiclReportLine(models.Model):
    _inherit = 'account.financial.dynamic.report.line'

    def _put_columns_together(self, data, domain_ids):
        res = dict((domain_id, []) for domain_id in domain_ids)
        for period in data:
            line_balance = 0
            debit_credit = False
            if 'debit' in period['line']:
                debit_credit = True
            for domain_id in domain_ids:
                if debit_credit:
                    res[domain_id].append(period.get(domain_id, {'debit': 0})['debit'])
                    res[domain_id].append(period.get(domain_id, {'credit': 0})['credit'])
                if len(domain_ids) > 1:
                    if domain_id != 'line':
                        res[domain_id].append(period.get(domain_id, {'balance': 0})['balance'])
                        line_balance += period.get(domain_id, {'balance': 0})['balance']
                else:
                    res[domain_id].append(period.get(domain_id, {'balance': 0})['balance'])
            if 'line' in res and len(domain_ids) > 1:
                res['line'].append(line_balance)
        return res

    def _get_with_statement(self, financial_report):
        sql = ''
        params = []
        if financial_report in [self.env.ref('to_account_reports.af_dynamic_report_cashsummary0'), self.env.ref('to_account_reports_l10n_vn.af_dynamic_report_cashsummary_vn')]:
            return sql, params
        else:
            return super(AccountFinanciaDynamiclReportLine, self)._get_with_statement(financial_report)

    def _divide_line(self, line, financial_report=False):
        res = super(AccountFinanciaDynamiclReportLine, self)._divide_line(line, financial_report)
        if financial_report and financial_report.id == self.env.ref('to_account_reports_l10n_vn.af_dynamic_report_profitandloss_vn').id:
            res[1].update({
                'name': line['name'],
                'level': line['level']
                })
        return res
