from datetime import timedelta, datetime
from odoo import models, api, fields, _


class Report_L10n_Vn_S38dn(models.AbstractModel):
    _name = 'report.to_account_reports_l10n_vn.report_s38dn'
    _inherit = 'report.l10n_vn.common'
    _description = 'Vietnam S38-DN Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        res = super(Report_L10n_Vn_S38dn, self)._get_report_values(docids, data)
        target_type = 'target_type' in data['form'] and data['form']['target_type'] or False
        if target_type == 'account':
            res['account_ids'] = 'account_ids' in data['form'] and (', '.join(self.env['account.account'].browse(data['form']['account_ids']).mapped('code'))) or ''
        else:
            res['journal_ids'] = ', '.join(self.env['account.journal'].browse(data['form']['journal_ids']).mapped('code'))
        res['partner_ids'] = 'partner_ids' in data['form'] and ', '.join(self.env['res.partner'].browse(data['form']['partner_ids']).mapped('name')) or ''
        res['today'] = fields.Date.today()
        return res

    def group_by_account_id(self):
        accounts = {}
        ctx = self.env.context
        ctx_date_from = ctx.get('date_from')
        company = self.env.company
        results = self.do_query()
        initial_bal_date_to = fields.Date.from_string(ctx_date_from) + timedelta(days=-1)
        initial_bal_results = self.with_context(
            date_from=ctx_date_from and company.compute_fiscalyear_dates(datetime.strptime(ctx_date_from, '%Y-%m-%d'))['date_from'] or None,
            strict_range=False,
            date_to=initial_bal_date_to
            ).do_query()

        if not results:
            for account_id, result in initial_bal_results.items():
                default_result = {'balance': 0, 'amount_currency': 0, 'debit': 0, 'credit': 0}
                account = self.env['account.account'].browse(account_id)
                accounts[account] = default_result
                accounts[account]['lines'] = []
                accounts[account]['initial_bal'] = initial_bal_results.get(account.id, default_result)
            return accounts

        for account_id, result in results.items():
            account = self.env['account.account'].browse(account_id)
            accounts[account] = result
            accounts[account]['initial_bal'] = initial_bal_results.get(account.id, {'balance': 0, 'amount_currency': 0, 'debit': 0, 'credit': 0})
            aml_ctx = {}
            if ctx.get('date_from'):
                aml_ctx = {
                    'strict_range': True,
                    'date_from': ctx_date_from,
                }
            amlids = self.with_context(**aml_ctx)._do_query(account_id, group_by_account=False)
            sum_data = {}
            aml_ids = [x[0] for x in amlids]
            for aml_id in amlids:
                sum_data[aml_id[0]] = aml_id
            amls = self.env['account.move.line'].browse(aml_ids)
            accounts[account]['lines'] = []
            for aml in amls:
                line = aml
                line_vals = {
                    'line': line,
                    'sum_debit': sum_data[line.id][1],
                    'sum_credit': sum_data[line.id][2],
                    'sum_name': sum_data[line.id][3],
                }
                accounts[account]['lines'].append(line_vals)
        return accounts

    def _do_query(self, line_id, group_by_account=True):
        tables, where_clause, where_params = self.env['account.move.line']._query_get()
        line_clause = line_id and ' AND account_move_line.account_id = ' + str(line_id) or ''
        if group_by_account:
            sql = '''
            SELECT
                account_move_line.account_id,
                COALESCE(SUM(account_move_line.debit-account_move_line.credit), 0),
                SUM(account_move_line.amount_currency),
                SUM(account_move_line.debit),
                SUM(account_move_line.credit)
            FROM %s
            WHERE %s%s
            '''
            if group_by_account:
                sql += ' GROUP BY account_move_line.account_id'
            else:
                sql += ' GROUP BY account_move_line.account_id, account_move_line.date'
            # sql += ' ORDER BY account_move_line.date ASC'
            query = sql % (tables, where_clause, line_clause)
        else:
            sql = '''
            WITH grouped_lines AS(
                SELECT
                    account_move_line.move_id AS move_id,
                    MIN(account_move_line.id) AS id,
                    account_move_line.date AS date,
                    SUM(account_move_line.debit) AS sum_debit,
                    SUM(account_move_line.credit) AS sum_credit,
                    string_agg(DISTINCT account_move_line.name, ',') AS sum_name
                FROM account_move_line
                    JOIN account_move account_move_line__move_id ON (account_move_line.move_id=account_move_line__move_id.id)
                    JOIN account_account acc ON (account_move_line.account_id = acc.id)
                    JOIN account_ctp_account_rel ctp on account_move_line.id = ctp.aml_id
                    JOIN account_account ctp_acc on ctp.account_id  = ctp_acc.id
                WHERE %s%s
                GROUP BY
                    account_move_line.move_id,
                    ctp_acc.code,
                    acc.code,
                    account_move_line.account_id,
                    account_move_line.date
                ORDER BY account_move_line.date ASC
                )
            SELECT id, sum_debit, sum_credit, sum_name FROM grouped_lines
            GROUP BY id, date, sum_debit, sum_credit, move_id, sum_name
            ORDER BY date ASC
            '''
            query = sql % (where_clause, line_clause)

        self.env.cr.execute(query, where_params)
        results = self.env.cr.fetchall()
        return results

    def do_query(self, line_id=None):
        results = self._do_query(line_id)
        # TODO: date should match the move line date instead of today
        date = self._context.get('date') or fields.Date.today()
        company = self.env['res.company'].browse(self._context.get('company_id')) or self.env.company
        used_currency = company.currency_id
        compute_table = {
            a.id: a.company_id.currency_id
            for a in self.env['account.account'].browse([k[0] for k in results]) if a.company_id.currency_id != used_currency
        }
        results = dict([(
            k[0], {
                'balance': compute_table[k[0]]._convert(k[1], used_currency, company, date) if k[0] in compute_table and not compute_table[k[0]].is_zero(k[1]) else k[1],
                'amount_currency': k[2],
                'debit': compute_table[k[0]]._convert(k[3], used_currency, company, date) if k[0] in compute_table and not compute_table[k[0]].is_zero(k[3]) else k[3],
                'credit': compute_table[k[0]]._convert(k[4], used_currency, company, date) if k[0] in compute_table and not compute_table[k[0]].is_zero(k[4]) else k[4],
            }
        ) for k in results])
        return results

    @api.model
    def _get_lines(self, data):
        ctx = data['form'].get('used_context', {})
        if ctx.get('account_ids'):
            ctx['account_ids'] = self.env['account.account'].browse(ctx['account_ids'])
        if ctx.get('partner_ids'):
            ctx['partner_ids'] = self.env['res.partner'].browse(ctx['partner_ids'])
        grouped_accounts = self.with_context(**ctx).group_by_account_id()
        sorted_accounts = sorted(grouped_accounts, key=lambda a: a.code)
        currency_id = self.env['res.company'].browse(data['form']['company_id'][0]).currency_id
        decimal_places = currency_id.decimal_places
        report_lines = []
        for account in sorted_accounts:
            debit = grouped_accounts[account]['debit']
            credit = grouped_accounts[account]['credit']
            initial_debit = grouped_accounts[account]['initial_bal']['debit']
            initial_credit = grouped_accounts[account]['initial_bal']['credit']
            report_lines.append({
                'type': 'account_title',
                'account_name': '%s %s' % (account.code, account.name),
            })
            report_lines.append({
                'type': 'account_init',
                'name': _('Opening Balance'),
                'account_id': '',
                'debit': 0,
                'credit': 0,
                'progress': initial_debit - initial_credit,
                'progress_debit': initial_debit,
                'progress_credit': initial_credit,
                'decimal_places': decimal_places,
            })
            amls = grouped_accounts[account]['lines']
            progress_debit = initial_debit
            progress_credit = initial_credit
            for aml in amls:
                line = aml.get('line', False)
                if line:
                    progress_debit = progress_debit + aml.get('sum_debit', 0.0)
                    progress_credit = progress_credit + aml.get('sum_credit', 0.0)
                    report_lines.append({
                        'type': 'move_line',
                        'name': aml.get('sum_name', ''),
                        'account_id': ','.join([account.code for account in line.ctp_account_ids]),
                        'date': line.date,
                        'debit': aml.get('sum_debit', 0.0),
                        'credit': aml.get('sum_credit', 0.0),
                        'progress_debit': progress_debit,
                        'progress_credit': progress_credit,
                        'progress': progress_debit - progress_credit,
                        'ref_name': line.move_id.name,
                        'ref_date': line.move_id.date,
                        'decimal_places': decimal_places,
                    })
            report_lines.append({
                'type': 'account_total',
                'name': _('Period Total'),
                'account_id': '',
                'debit': debit,
                'credit': credit,
                'progress_debit': 0,
                'progress_credit': 0,
                'progress': 0,
                'decimal_places': decimal_places,
            })
            report_lines.append({
                'type': 'account_end',
                'name': _('Ending Balance'),
                'account_id': '',
                'debit': 0,
                'credit': 0,
                'progress_debit': progress_debit,
                'progress_credit': progress_credit,
                'progress': progress_debit - progress_credit,
                'decimal_places': decimal_places,
            })
        return report_lines
