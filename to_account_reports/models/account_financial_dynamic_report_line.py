import copy
from odoo import models, fields, api, _
from odoo.tools.safe_eval import safe_eval
from odoo.tools.misc import formatLang
from odoo.tools import float_is_zero, ustr
from odoo.exceptions import ValidationError, UserError
from odoo.osv import expression
from datetime import datetime
from dateutil.relativedelta import relativedelta
from .formula_classes import FormulaLine, FormulaContext


class AccountFinancialDynamicReportLine(models.Model):
    _name = "account.financial.dynamic.report.line"
    _description = "Account Report Line"
    _order = "sequence"

    name = fields.Char('Section Name', translate=True)
    code = fields.Char('Code')
    report_code = fields.Char(string='Report Code', help="The code to show on the report if specified while the corresponding report of the line allows that")
    show_report_code = fields.Boolean(string='Show Report Code', compute='_compute_show_report_code', store=True,
                                      help="Technical field to indicate if the report code should display on the reports")
    report_note = fields.Char(string='Report Note', help="The note to show on the report if specified while the corresponding report of the line allows that")
    show_report_note = fields.Boolean(string='Show Report Note', compute='_compute_show_report_note', store=True,
                                      help="Technical field to indicate if the report note should display on the reports")
    show_on_pdf = fields.Boolean(string='Show On Report Printed', default=True,
                                 help="Technical field to indicate if this report line should display on pdf printed.")
    financial_report_id = fields.Many2one('account.financial.dynamic.report', 'Financial Report')
    parent_id = fields.Many2one('account.financial.dynamic.report.line', string='Parent')
    children_ids = fields.One2many('account.financial.dynamic.report.line', 'parent_id', string='Children')
    sequence = fields.Integer()

    domain = fields.Char(default=None)
    formulas = fields.Char()
    groupby = fields.Char("Group by", default=False)

    figure_type = fields.Selection([('float', 'Float'), ('percents', 'Percents'), ('no_unit', 'No Unit')],
                                   string='Type', default='float', required=True)
    green_on_positive = fields.Boolean('Is growth good when positive', default=True)
    level = fields.Integer(required=True)
    special_date_changer = fields.Selection([
        ('from_beginning', 'From the beginning'),
        ('to_beginning_of_period', 'At the beginning of the period'),
        ('normal', 'Use given dates'),
        ('strict_range', 'Force given dates for all accounts and account types'),
        ('from_fiscalyear', 'From the beginning of the fiscal year'),
    ], default='normal')
    show_domain = fields.Selection([
        ('always', 'Always'),
        ('never', 'Never'),
        ('foldable', 'Foldable')
        ], default='foldable')
    hide_if_zero = fields.Boolean(string='Hide if Zero', default=False)
    action_id = fields.Many2one('ir.actions.actions', string='Client Action')
#    report_code = fields.Char(string='Report Code', help='Code of an item witch will be shown in reports (if defined)')
    account_chart_template_id = fields.Many2one('account.chart.template', string='Account Chart Template', help="Leave empty to apply this rule no matter the"
                                                " company's chart template is. When specified, this rule is activated for all the companies of the given chart"
                                                " template.")
    duration_term = fields.Selection([
        ('normal', 'N/A'),
        ('duration_3m_orless', '3 Months or less'),
        ('duration_4mo_to_12mo', 'more than 3 month & less than 12 months'),
        ('duration_more_3mo', 'more than 3 months'),
        ('short_term', '12 months or less'),
        ('long_term', 'Non Current (more than 12 months)')], string='Duration Term', default='normal', required=True)
    duration_term_date_field = fields.Char(string='Duration Term Date Field', default='date_maturity', required=True,
                                           help="The date field of journal item for usage with Duration Term. Default value is date_maturity (Due Date)")
    duration_term_direction = fields.Selection([('past', 'To the Past'), ('future', 'To the Future')], string='Duration Term Direction',
                                               help="The direction of the Duration Term which is either:\n"
                                               "- To the Past: the condition will compare the data from the past.\n"
                                               "- To the Future: the condition will compare the data to the future\n")
    duration_term_base_on = fields.Selection([('all', 'All'), ('not_liquidity', 'Not liquidity'), ('liquidity', 'Liquidity')], string='Duration Term Base On', default='all',
                                             help="Khi tính toán các chỉ tiêu có liên quan dài hạn, ngắn hạn, có một số chỉ tiêu như Khách hàng trả trước,\n"
                                             "hoặc Trả trước người bán (chọn Liquidity) thì cần lấy due date của các bút toán mà tài khoản đối ứng của nó có kiểu Thanh khoản\n"
                                             "(bút toán liên quan đến thanh toán) để tính toán. Trường hợp chọn Not liquidity thì sẽ lấy date due của các bút toán có tài\n"
                                             "khoản đối ứng không thuộc kiểu thanh khoản để tính toán.")

    _sql_constraints = [
        ('code_uniq', 'unique (code)', "A report line with the same code already exists."),
    ]

    @api.constrains('duration_term_date_field')
    def _check_date_field_exist(self):
        AccountMoveLine = self.env['account.move.line']
        for r in self:
            if not hasattr(AccountMoveLine, r.duration_term_date_field):
                raise UserError(_("Journal Items do not have the field %s. Please specify another value for the field Duration Term Date Field")
                                % (r.duration_term_date_field,))

    @api.constrains('code')
    def _code_constrains(self):
        if self.code and self.code.strip().lower() in __builtins__.keys():
            raise ValidationError('The code "%s" is invalid on line with name "%s"' % (self.code, self.name))

    @api.depends('financial_report_id', 'financial_report_id.show_report_code', 'report_code', 'parent_id.show_report_code')
    def _compute_show_report_code(self):
        for r in self:
            if r.financial_report_id:
                r.show_report_code = True if r.financial_report_id.show_report_code else False
            else:
                r.show_report_code = True if r.parent_id and r.parent_id.show_report_code else False

    @api.onchange('duration_term')
    def _onchange_duration_term(self):
        if self.duration_term == 'normal':
            self.duration_term_direction = False

    @api.depends('financial_report_id', 'financial_report_id.show_report_note', 'report_note', 'parent_id.show_report_note')
    def _compute_show_report_note(self):
        for r in self:
            if r.financial_report_id:
                r.show_report_note = True if r.financial_report_id.show_report_note else False
            else:
                r.show_report_note = True if r.parent_id and r.parent_id.show_report_note else False

    def _get_copied_code(self):
        self.ensure_one()
        code = self.code + '_COPY'
        while self.search_count([('code', '=', code)]) > 0:
            code += '_COPY'
        return code

    def copy_hierarchy(self, report_id=None, copied_report_id=None, parent_id=None, code_mapping=None):
        self.ensure_one()
        if code_mapping is None:
            code_mapping = {}
        # If the line points to the old report, replace with the new one.
        # Otherwise, cut the link to another financial report.
        if report_id and copied_report_id and self.financial_report_id.id == report_id.id:
            financial_report_id = copied_report_id.id
        else:
            financial_report_id = None
        copy_line_id = self.copy({
            'financial_report_id': financial_report_id,
            'parent_id': parent_id and parent_id.id,
            'code': self.code and self._get_copied_code(),
        })
        # Keep track of old_code -> new_code in a mutable dict
        if self.code:
            code_mapping[self.code] = copy_line_id.code
        # Copy children
        for line in self.children_ids:
            line.copy_hierarchy(parent_id=copy_line_id, code_mapping=code_mapping)
        # Update formulas
        if self.formulas:
            copied_formulas = self.formulas
            for k, v in code_mapping.items():
                for field in ['debit', 'credit', 'balance', 'amount_residual']:
                    suffix = '.' + field
                    copied_formulas = copied_formulas.replace(k + suffix, v + suffix)
            copy_line_id.formulas = copied_formulas

    def _query_get_select_sum(self, currency_table):
        extra_params = []
        select = '''
            COALESCE(SUM(\"account_move_line\".balance), 0) AS balance,
            COALESCE(SUM(\"account_move_line\".amount_residual), 0) AS amount_residual,
            COALESCE(SUM(\"account_move_line\".debit), 0) AS debit,
            COALESCE(SUM(\"account_move_line\".credit), 0) AS credit
        '''
        if currency_table:
            select = 'COALESCE(SUM(CASE '
            for currency_id, rate in currency_table.items():
                extra_params += [currency_id, rate]
                select += 'WHEN \"account_move_line\".company_currency_id = %s THEN \"account_move_line\".balance * %s '
            select += 'ELSE \"account_move_line\".balance END), 0) AS balance, COALESCE(SUM(CASE '
            for currency_id, rate in currency_table.items():
                extra_params += [currency_id, rate]
                select += 'WHEN \"account_move_line\".company_currency_id = %s THEN \"account_move_line\".amount_residual * %s '
            select += 'ELSE \"account_move_line\".amount_residual END), 0) AS amount_residual, COALESCE(SUM(CASE '
            for currency_id, rate in currency_table.items():
                extra_params += [currency_id, rate]
                select += 'WHEN \"account_move_line\".company_currency_id = %s THEN \"account_move_line\".debit * %s '
            select += 'ELSE \"account_move_line\".debit END), 0) AS debit, COALESCE(SUM(CASE '
            for currency_id, rate in currency_table.items():
                extra_params += [currency_id, rate]
                select += 'WHEN \"account_move_line\".company_currency_id = %s THEN \"account_move_line\".credit * %s '
            select += 'ELSE \"account_move_line\".credit END), 0) AS credit'

        return select, extra_params

    def _get_with_statement(self, financial_report):
        sql = ''
        params = []

        if financial_report == self.env.ref('to_account_reports.af_dynamic_report_cashsummary0'):
            return sql, params
            # bank_journals = self.env['account.journal'].search([('type', 'in', ('bank', 'cash'))])
            # bank_accounts = bank_journals.mapped('default_debit_account_id') + bank_journals.mapped('default_credit_account_id')
            #
            # # Get moves having a line using a bank account.
            # self._cr.execute('SELECT DISTINCT(move_id) FROM account_move_line WHERE account_id IN %s', [tuple(bank_accounts.ids)])
            # bank_move_ids = tuple([r[0] for r in self.env.cr.fetchall()])
            #
            # # Get available fields.
            # replace_columns = {
            #     'date': 'ref.date',
            # }
            # columns = []
            # columns_2 = []
            # for name, field in self.env['account.move.line']._fields.items():
            #     if not(field.store and field.type not in ('one2many', 'many2many')):
            #         continue
            #     columns.append('\"account_move_line\".%s' % name)
            #     if name in replace_columns:
            #         columns_2.append(replace_columns.get(name))
            #     else:
            #         columns_2.append('\"account_move_line\".%s' % name)
            # select_clause_1 = ', '.join(columns)
            # select_clause_2 = ', '.join(columns_2)
            #
            # # Fake domain to always get the join to the account_move_line__move_id table.
            # fake_domain = [('move_id.id', '!=', None)]
            # sub_tables, sub_where_clause, sub_where_params = self.env['account.move.line']._query_get(domain=fake_domain)
            # tables, where_clause, where_params = self.env['account.move.line']._query_get(domain=fake_domain + safe_eval(self.domain))
            #
            # sql = '''
            #     WITH account_move_line AS (
            #         WITH payment_table AS (
            #             SELECT
            #                 aml.id,
            #                 "account_move_line".move_id,
            #                 "account_move_line".date,
            #                 CASE WHEN aml.balance = 0 THEN
            #                     0 ELSE part.amount / ABS("account_move_line__move_id".amount)
            #                 END AS matched_percentage
            #             FROM account_partial_reconcile part
            #             LEFT JOIN account_move_line aml ON aml.id = part.debit_move_id
            #             LEFT JOIN account_account acc ON aml.account_id = acc.id
            #             LEFT JOIN account_move am ON aml.move_id = am.id, ''' + sub_tables + '''
            #             WHERE part.credit_move_id = "account_move_line".id
            #             AND acc.reconcile
            #             AND aml.move_id IN %s
            #             AND ''' + sub_where_clause + '''
            #
            #             UNION ALL
            #
            #             SELECT
            #                 aml.id,
            #                 "account_move_line".move_id,
            #                 "account_move_line".date,
            #                 CASE WHEN aml.balance = 0 THEN
            #                     0 ELSE part.amount / ABS("account_move_line__move_id".amount)
            #                 END AS matched_percentage
            #             FROM account_partial_reconcile part
            #             LEFT JOIN account_move_line aml ON aml.id = part.credit_move_id
            #             LEFT JOIN account_account acc ON aml.account_id = acc.id
            #             LEFT JOIN account_move am ON aml.move_id = am.id, ''' + sub_tables + '''
            #             WHERE part.debit_move_id = "account_move_line".id
            #             AND acc.reconcile
            #             AND aml.move_id IN %s
            #             AND ''' + sub_where_clause + '''
            #         )
            #
            #         SELECT ''' + select_clause_2 + '''
            #         FROM ''' + tables + '''
            #         RIGHT JOIN payment_table ref ON ("account_move_line".move_id = ref.move_id)
            #         LEFT JOIN account_account acc ON "account_move_line".account_id = acc.id
            #         WHERE acc.internal_type = 'other'
            #         AND "account_move_line".move_id NOT IN %s
            #         AND ''' + where_clause + '''
            #
            #         UNION ALL
            #
            #         SELECT ''' + select_clause_1 + '''
            #         FROM ''' + tables + '''
            #         WHERE "account_move_line".move_id IN %s
            #         AND ''' + where_clause + '''
            #     )
            # '''
            # params = [tuple(bank_move_ids)] + sub_where_params + [tuple(bank_move_ids)] + sub_where_params\
            #          +[tuple(bank_move_ids)] + where_params + [tuple(bank_move_ids)] + where_params
        return sql, params

    def _compute_line(self, currency_table, financial_report, group_by=None, domain=[]):
        domain = domain and safe_eval(ustr(domain))
        for index, condition in enumerate(domain):
            if condition[0].startswith('tax_ids.'):
                new_condition = (condition[0].partition('.')[2], condition[1], condition[2])
                taxes = self.env['account.tax'].with_context(active_test=False).search([new_condition])
                domain[index] = ('tax_ids', 'in', taxes.ids)
        tables, where_clause, where_params = self.env['account.move.line']._query_get(domain=domain)
        if financial_report.tax_report:
            where_clause += ''' AND "account_move_line".tax_exigible = 't' '''

        line = self
        financial_report = False

        while(not financial_report):
            financial_report = line.financial_report_id
            if not line.parent_id:
                break
            line = line.parent_id

        sql, params = self._get_with_statement(financial_report)

        select, select_params = self._query_get_select_sum(currency_table)
        where_params = params + select_params + where_params

        company_ids = self._context.get('company_ids', False)
        filter_company = self.env['res.company']
        if company_ids:
            filter_company = self.env['res.company'].search([('id', '=', company_ids[0])])
        if (self.env.context.get('sum_if_pos') or self.env.context.get('sum_if_neg')) and group_by:
            sql = sql + "SELECT account_move_line." + group_by + " as " + group_by + "," + select + " FROM " + tables + " WHERE " + where_clause + " GROUP BY account_move_line." + group_by
            self.env.cr.execute(sql, where_params)
            res = {'balance': 0, 'debit': 0, 'credit': 0, 'amount_residual': 0}
            for row in self.env.cr.dictfetchall():
                if (row['balance'] > 0 and self.env.context.get('sum_if_pos')) or (row['balance'] < 0 and self.env.context.get('sum_if_neg')):
                    for field in ['debit', 'credit', 'balance', 'amount_residual']:
                        res[field] += row[field]
            res['currency_id'] = filter_company and filter_company.currency_id.id or self.env.company.currency_id.id
            return res

        sql = sql + "SELECT " + select + " FROM " + tables + " WHERE " + where_clause
        self.env.cr.execute(sql, where_params)
        results = self.env.cr.dictfetchall()[0]
        results['currency_id'] = filter_company and filter_company.currency_id.id or self.env.company.currency_id.id
        return results

    def _compute_date_range(self):
        date_from = self._context.get('date_from', False)
        date_to = self._context.get('date_to', False)

        strict_range = self.special_date_changer == 'strict_range'
        if self.special_date_changer == 'from_beginning':
            date_from = False
        if self.special_date_changer == 'to_beginning_of_period' and date_from:
            date_tmp = datetime.strptime(self._context['date_from'], "%Y-%m-%d") - relativedelta(days=1)
            date_to = date_tmp.strftime('%Y-%m-%d')
            date_from = False
        if self.special_date_changer == 'from_fiscalyear' and date_to:
            date_tmp = datetime.strptime(date_to, '%Y-%m-%d')
            date_tmp = self.env.company.compute_fiscalyear_dates(date_tmp)['date_from']
            date_from = date_tmp.strftime('%Y-%m-%d')
            strict_range = True
        return date_from, date_to, strict_range

    def report_move_lines_action(self):
        domain = safe_eval(self.domain)
        if 'date_from' in self.env.context.get('context', {}):
            if self.env.context['context'].get('date_from'):
                domain = expression.AND([domain, [('date', '>=', self.env.context['context']['date_from'])]])
            if self.env.context['context'].get('date_to'):
                domain = expression.AND([domain, [('date', '<=', self.env.context['context']['date_to'])]])
            if self.env.context['context'].get('state', 'all') == 'posted':
                domain = expression.AND([domain, [('move_id.state', '=', 'posted')]])
            if self.env.context['context'].get('company_ids'):
                domain = expression.AND([domain, [('company_id', 'in', self.env.context['context']['company_ids'])]])
        return {'type': 'ir.actions.act_window',
                'name': 'Journal Items (%s)' % self.name,
                'res_model': 'account.move.line',
                'view_mode': 'tree,form',
                'domain': domain,
                }

    @api.constrains('groupby')
    def _check_same_journal(self):
        for r in self:
            if r.groupby and r.groupby not in self.env['account.move.line']:
                raise ValidationError(_("Groupby should be a journal item field"))

    @api.model
    def _prepare_duration_term_domain(self, date_to):
        domain = []
        if self.duration_term_direction == 'past':
            date_due = datetime.strptime(date_to, "%Y-%m-%d") - relativedelta(months=12)
            date_midle = datetime.strptime(date_to, "%Y-%m-%d") - relativedelta(months=3)
            # Do vấn đề cần xem các chỉ tiêu về phải thu, phải trả trong quá khứ nên ta phải lấy dữ liệu theo balance thay vì amount_residual
            # Do đó cần phải xét đến cả các bút toán có số dư bên nợ và bên có của tài khoản phải thu, phải trả
            # Các bút toán liên quan đến thanh toán thì cần phải xét tới bút toán đối soát với nó (matched_move_line_id) có thuộc cùng kiểu ngắn hạn (hoặc dài hạn) đang xét hay không nữa.
            if self.duration_term == 'short_term':  # <= 12 months
                if self.duration_term_base_on == 'not_liquidity':
                    domain += ['|', '|',
                                    '&', ('ctp_account_ids.user_type_id.type', '!=', 'liquidity'), (self.duration_term_date_field, '>=', date_due.strftime('%Y-%m-%d')),
                                    '&', ('ctp_account_ids.user_type_id.type', '=', 'liquidity'),
                                        '|', '|', ('matched_debit_ids.debit_move_id.' + self.duration_term_date_field, '>=', date_due.strftime('%Y-%m-%d')),
                                            ('matched_credit_ids.credit_move_id.' + self.duration_term_date_field, '>=', date_due.strftime('%Y-%m-%d')),
                                            '&', '&', ('matched_debit_ids', '=', False), ('matched_credit_ids', '=', False),
                                            (self.duration_term_date_field, '>=', date_due.strftime('%Y-%m-%d')),
                                    (self.duration_term_date_field, '=', False)]
                elif self.duration_term_base_on == 'liquidity':
                    domain += ['|', '|',
                                    '&', ('ctp_account_ids.user_type_id.type', '=', 'liquidity'), (self.duration_term_date_field, '>=', date_due.strftime('%Y-%m-%d')),
                                    '&', ('ctp_account_ids.user_type_id.type', '!=', 'liquidity'),
                                        '|', '|', ('matched_debit_ids.debit_move_id.' + self.duration_term_date_field, '>=', date_due.strftime('%Y-%m-%d')),
                                            ('matched_credit_ids.credit_move_id.' + self.duration_term_date_field, '>=', date_due.strftime('%Y-%m-%d')),
                                            '&', '&', ('matched_debit_ids', '=', False), ('matched_credit_ids', '=', False),
                                            (self.duration_term_date_field, '>=', date_due.strftime('%Y-%m-%d')),
                                    (self.duration_term_date_field, '=', False)]
                else:
                    domain += ['|', (self.duration_term_date_field, '>=', date_due.strftime('%Y-%m-%d')), (self.duration_term_date_field, '=', False)]
            elif self.duration_term == 'long_term':  # > 12 months
                if self.duration_term_base_on == 'not_liquidity':
                    domain += ['|',
                                    '&', ('ctp_account_ids.user_type_id.type', '!=', 'liquidity'), (self.duration_term_date_field, '<', date_due.strftime('%Y-%m-%d')),
                                    '&', ('ctp_account_ids.user_type_id.type', '=', 'liquidity'),
                                        '|', '|', ('matched_debit_ids.debit_move_id.' + self.duration_term_date_field, '<', date_due.strftime('%Y-%m-%d')),
                                            ('matched_credit_ids.credit_move_id.' + self.duration_term_date_field, '<', date_due.strftime('%Y-%m-%d')),
                                            '&', '&', ('matched_debit_ids', '=', False), ('matched_credit_ids', '=', False),
                                            (self.duration_term_date_field, '<', date_due.strftime('%Y-%m-%d'))]
                elif self.duration_term_base_on == 'liquidity':
                    domain += ['|',
                                    '&', ('ctp_account_ids.user_type_id.type', '=', 'liquidity'), (self.duration_term_date_field, '<', date_due.strftime('%Y-%m-%d')),
                                    '&', ('ctp_account_ids.user_type_id.type', '!=', 'liquidity'),
                                        '|', '|', ('matched_debit_ids.debit_move_id.' + self.duration_term_date_field, '<', date_due.strftime('%Y-%m-%d')),
                                            ('matched_credit_ids.credit_move_id.' + self.duration_term_date_field, '<', date_due.strftime('%Y-%m-%d')),
                                            '&', '&', ('matched_debit_ids', '=', False), ('matched_credit_ids', '=', False),
                                            (self.duration_term_date_field, '<', date_due.strftime('%Y-%m-%d'))]
                else:
                    domain += [(self.duration_term_date_field, '<', date_due.strftime('%Y-%m-%d'))]
            elif self.duration_term == 'duration_3m_orless':  # <= 3 months
                domain += [(self.duration_term_date_field, '>=', date_midle.strftime('%Y-%m-%d'))]
            elif self.duration_term == 'duration_4mo_to_12mo':  # > 3 months and <= 12 months
                domain += [(self.duration_term_date_field, '>=', date_due.strftime('%Y-%m-%d')),
                           (self.duration_term_date_field, '<', date_midle.strftime('%Y-%m-%d'))]
            elif self.duration_term == 'duration_more_3mo':  # > 3 months
                domain += [(self.duration_term_date_field, '<', date_midle.strftime('%Y-%m-%d'))]
        else:
            date_due = datetime.strptime(date_to, "%Y-%m-%d") + relativedelta(months=12)
            date_midle = datetime.strptime(date_to, "%Y-%m-%d") + relativedelta(months=3)

            if self.duration_term == 'short_term':  # <= 12 months
                if self.duration_term_base_on == 'not_liquidity':
                    domain += ['|', '|',
                                    '&', ('ctp_account_ids.user_type_id.type', '!=', 'liquidity'), (self.duration_term_date_field, '<=', date_due.strftime('%Y-%m-%d')),
                                    '&', ('ctp_account_ids.user_type_id.type', '=', 'liquidity'),
                                        '|', '|', ('matched_debit_ids.debit_move_id.' + self.duration_term_date_field, '<=', date_due.strftime('%Y-%m-%d')),
                                            ('matched_credit_ids.credit_move_id.' + self.duration_term_date_field, '<=', date_due.strftime('%Y-%m-%d')),
                                            '&', '&', ('matched_debit_ids', '=', False), ('matched_credit_ids', '=', False),
                                            (self.duration_term_date_field, '<=', date_due.strftime('%Y-%m-%d')),
                                    (self.duration_term_date_field, '=', False)]
                elif self.duration_term_base_on == 'liquidity':
                    domain += ['|', '|',
                                    '&', ('ctp_account_ids.user_type_id.type', '=', 'liquidity'), (self.duration_term_date_field, '<=', date_due.strftime('%Y-%m-%d')),
                                    '&', ('ctp_account_ids.user_type_id.type', '!=', 'liquidity'),
                                        '|', '|', ('matched_debit_ids.debit_move_id.' + self.duration_term_date_field, '<=', date_due.strftime('%Y-%m-%d')),
                                            ('matched_credit_ids.credit_move_id.' + self.duration_term_date_field, '<=', date_due.strftime('%Y-%m-%d')),
                                            '&', '&', ('matched_debit_ids', '=', False), ('matched_credit_ids', '=', False),
                                            (self.duration_term_date_field, '<=', date_due.strftime('%Y-%m-%d')),
                                    (self.duration_term_date_field, '=', False)]
                else:
                    domain += ['|', (self.duration_term_date_field, '<=', date_due.strftime('%Y-%m-%d')), (self.duration_term_date_field, '=', False)]
            elif self.duration_term == 'long_term':  # > 12 months
                if self.duration_term_base_on == 'not_liquidity':
                    domain += ['|',
                                    '&', ('ctp_account_ids.user_type_id.type', '!=', 'liquidity'), (self.duration_term_date_field, '>', date_due.strftime('%Y-%m-%d')),
                                    '&', ('ctp_account_ids.user_type_id.type', '=', 'liquidity'),
                                        '|', '|', ('matched_debit_ids.debit_move_id.' + self.duration_term_date_field, '>', date_due.strftime('%Y-%m-%d')),
                                            ('matched_credit_ids.credit_move_id.' + self.duration_term_date_field, '>', date_due.strftime('%Y-%m-%d')),
                                            '&', '&', ('matched_debit_ids', '=', False), ('matched_credit_ids', '=', False),
                                            (self.duration_term_date_field, '>', date_due.strftime('%Y-%m-%d'))]
                elif self.duration_term_base_on == 'liquidity':
                    domain += ['|',
                                    '&', ('ctp_account_ids.user_type_id.type', '=', 'liquidity'), (self.duration_term_date_field, '>', date_due.strftime('%Y-%m-%d')),
                                    '&', ('ctp_account_ids.user_type_id.type', '!=', 'liquidity'),
                                        '|', '|', ('matched_debit_ids.debit_move_id.' + self.duration_term_date_field, '>', date_due.strftime('%Y-%m-%d')),
                                            ('matched_credit_ids.credit_move_id.' + self.duration_term_date_field, '>', date_due.strftime('%Y-%m-%d')),
                                            '&', '&', ('matched_debit_ids', '=', False), ('matched_credit_ids', '=', False),
                                            (self.duration_term_date_field, '>', date_due.strftime('%Y-%m-%d'))]
                else:
                    domain += [(self.duration_term_date_field, '>', date_due.strftime('%Y-%m-%d'))]
            elif self.duration_term == 'duration_3m_orless':  # <= 3 months
                domain += [(self.duration_term_date_field, '<=', date_midle.strftime('%Y-%m-%d'))]
            elif self.duration_term == 'duration_4mo_to_12mo':  # > 3 months and <= 12 months
                domain += [(self.duration_term_date_field, '>', date_midle.strftime('%Y-%m-%d')),
                           (self.duration_term_date_field, '<=', date_due.strftime('%Y-%m-%d'))]
            elif self.duration_term == 'duration_more_3mo':  # > 3 months
                domain += [(self.duration_term_date_field, '>', date_midle.strftime('%Y-%m-%d'))]
        return domain

    def _prepare_legal_report_off_domain(self):
        """
        For potential inheritance
        """
        return []

    def _get_sum(self, currency_table, financial_report, field_names=None):
        ''' Returns the sum of the amls in the domain '''
        if not field_names:
            field_names = ['debit', 'credit', 'balance', 'amount_residual']
        res = dict((fn, 0.0) for fn in field_names)
        if self.domain:
            date_from, date_to, strict_range = \
                self._compute_date_range()
            domain = safe_eval(ustr(self.domain))
            domain = self._prepare_legal_report_off_domain() + domain
            if date_to:
                domain = self._prepare_duration_term_domain(date_to) + domain
            res = self.with_context(strict_range=strict_range, date_from=date_from, date_to=date_to)._compute_line(currency_table, financial_report, group_by=self.groupby, domain=domain)
        return res

    def _get_balance(self, linesDict, currency_table, financial_report, field_names=None):
        self.ensure_one()
        if not field_names:
            field_names = ['debit', 'credit', 'balance']
        res = dict((fn, 0.0) for fn in field_names)
        c = FormulaContext(self.env['account.financial.dynamic.report.line'], linesDict, currency_table, financial_report, self)
        if self.formulas:
            for f in self.formulas.split(';'):
                [field, formula] = f.split('=')
                field = field.strip()
                if field in field_names:
                    try:
                        res[field] = safe_eval(formula, c, nocopy=True)
                    except ValueError as err:
                        if 'division by zero' in err.args[0]:
                            res[field] = 0
                        else:
                            raise err
                    except ZeroDivisionError:
                        res[field] = 0
        return res

    def _get_rows_count(self):
        groupby = self.groupby or 'id'
        if groupby not in self.env['account.move.line']:
            raise ValueError(_('Groupby should be a field from account.move.line'))

        if self.domain:
            domain = safe_eval(ustr(self.domain))
        else:
            domain = []

        domain = self._prepare_legal_report_off_domain() + domain

        date_from, date_to, strict_range = self._compute_date_range()
        if date_to:
            domain = self._prepare_duration_term_domain(date_to) + domain
        tables, where_clause, where_params = self.env['account.move.line'].with_context(strict_range=strict_range, date_from=date_from, date_to=date_to)._query_get(domain=domain)

        query = 'SELECT count(distinct(account_move_line.' + groupby + ')) FROM ' + tables + 'WHERE' + where_clause
        self.env.cr.execute(query, where_params)
        return self.env.cr.dictfetchall()[0]['count']

    def _get_value_from_context(self):
        if self.env.context.get('financial_report_line_values'):
            return self.env.context.get('financial_report_line_values').get(self.code, 0)
        return 0

    def _format(self, value):
        if self.env.context.get('no_format'):
            return value
        company_ids = self._context.get('company_ids', False)
        filter_company = self.env['res.company']
        if company_ids:
            filter_company = self.env['res.company'].search([('id', '=', company_ids[0])])
        value['no_format_name'] = value['name']
        if self.figure_type == 'float':
            currency_id = filter_company and filter_company.currency_id or self.env.company.currency_id
            if currency_id.is_zero(value['name']):
                # don't print -0.0 in reports
                value['name'] = abs(value['name'])
            value['name'] = formatLang(self.env, value['name'], currency_obj=currency_id)
            return value
        if self.figure_type == 'percents':
            value['name'] = str(round(value['name'] * 100, 1)) + '%'
            return value
        value['name'] = round(value['name'], 1)
        return value

    def _get_gb_name(self, gb_id):
        if self.groupby and self.env['account.move.line']._fields[self.groupby].relational:
            relation = self.env['account.move.line']._fields[self.groupby].comodel_name
            gb = self.env[relation].browse(gb_id)
            return gb.name_get()[0][1] if gb and gb.exists() else _('Undefined')
        return gb_id

    def _build_cmp(self, balance, comp):
        if comp != 0:
            res = round((balance - comp) / comp * 100, 1)
            if (res > 0) != (self.green_on_positive and comp > 0):
                return {'name': str(res) + '%', 'class': 'number color-red'}
            else:
                return {'name': str(res) + '%', 'class': 'number color-green'}
        else:
            return {'name': _('n/a'), 'class': 'number'}

    def _split_formulas(self):
        result = {}
        if self.formulas:
            for f in self.formulas.split(';'):
                [column, formula] = f.split('=')
                column = column.strip()
                result.update({column: formula})
        return result

    def _eval_formula(self, financial_report, debit_credit, currency_table, linesDict):
        debit_credit = debit_credit and financial_report.debit_credit
        formulas = self._split_formulas()
        if self.code and self.code in linesDict:
            res = linesDict[self.code]
        elif formulas and formulas['balance'].strip() == 'count_rows' and self.groupby:
            return {'line': {'balance': self._get_rows_count()}}
        elif formulas and formulas['balance'].strip() == 'from_context':
            return {'line': {'balance': self._get_value_from_context()}}
        else:
            res = FormulaLine(self, currency_table, financial_report, linesDict=linesDict)
        vals = {}
        vals['balance'] = res.balance
        if debit_credit:
            vals['credit'] = res.credit
            vals['debit'] = res.debit

        results = {}
        if self.domain and self.groupby and self.show_domain != 'never':
            domain = safe_eval(ustr(self.domain))
            domain = self._prepare_legal_report_off_domain() + domain
            if self._context['date_to']:
                domain = self._prepare_duration_term_domain(self._context['date_to']) + domain

            aml_obj = self.env['account.move.line']
            tables, where_clause, where_params = aml_obj._query_get(domain=domain)
            sql, params = self._get_with_statement(financial_report)
            if financial_report.tax_report:
                where_clause += ''' AND "account_move_line".tax_exigible = 't' '''

            groupby = self.groupby or 'id'
            if groupby not in self.env['account.move.line']:
                raise ValueError(_('Groupby should be a field from account.move.line'))
            select, select_params = self._query_get_select_sum(currency_table)
            params += select_params
            sql = sql + "SELECT \"account_move_line\"." + groupby + ", " + select + " FROM " + tables + " WHERE " + where_clause + " GROUP BY \"account_move_line\"." + groupby

            params += where_params
            self.env.cr.execute(sql, params)
            results = self.env.cr.fetchall()
            results = dict([(k[0], {'balance': k[1], 'amount_residual': k[2], 'debit': k[3], 'credit': k[4]}) for k in results])
            c = FormulaContext(self.env['account.financial.dynamic.report.line'], linesDict, currency_table, financial_report, only_sum=True)
            if formulas:
                for key in results:
                    c['sum'] = FormulaLine(results[key], currency_table, financial_report, type='not_computed')
                    c['sum_if_pos'] = FormulaLine(results[key]['balance'] >= 0.0 and results[key] or {'balance': 0.0}, currency_table, financial_report, type='not_computed')
                    c['sum_if_neg'] = FormulaLine(results[key]['balance'] <= 0.0 and results[key] or {'balance': 0.0}, currency_table, financial_report, type='not_computed')
                    for col, formula in formulas.items():
                        if col in results[key]:
                            results[key][col] = safe_eval(formula, c, nocopy=True)
            to_del = []
            for key in results:
                if self.env.company.currency_id.is_zero(results[key]['balance']):
                    to_del.append(key)
            for key in to_del:
                del results[key]

        results.update({'line': vals})
        return results

    def _put_columns_together(self, data, domain_ids):
        res = dict((domain_id, []) for domain_id in domain_ids)
        for period in data:
            debit_credit = False
            if 'debit' in period['line']:
                debit_credit = True
            for domain_id in domain_ids:
                if debit_credit:
                    res[domain_id].append(period.get(domain_id, {'debit': 0})['debit'])
                    res[domain_id].append(period.get(domain_id, {'credit': 0})['credit'])
                res[domain_id].append(period.get(domain_id, {'balance': 0})['balance'])
        return res

    def get_lines(self, financial_report, currency_table, options, linesDicts):
        final_result_table = []
        comparison_table = [options.get('date')]
        comparison_table += options.get('comparison') and options['comparison'].get('periods', []) or []
        currency_precision = self.env.company.currency_id.rounding
        # build comparison table
        for line in self:
            res = []
            debit_credit = len(comparison_table) == 1
            domain_ids = {'line'}
            k = 0
            for period in comparison_table:
                date_from = period.get('date_from', False)
                date_to = period.get('date_to', False) or period.get('date', False)
                date_from, date_to, strict_range = line.with_context(date_from=date_from, date_to=date_to)._compute_date_range()
                r = line.with_context(date_from=date_from, date_to=date_to, strict_range=strict_range)._eval_formula(financial_report, debit_credit, currency_table, linesDicts[k])
                debit_credit = False
                res.append(r)
                domain_ids.update(r)
                k += 1
            res = line._put_columns_together(res, domain_ids)
            if line.hide_if_zero and all([float_is_zero(k, precision_rounding=currency_precision) for k in res['line']]):
                continue

            # Post-processing ; creating line dictionnary, building comparison, computing total for extended, formatting
            report_code = line.report_code if line.show_report_code else False
            report_note = line.report_note if line.show_report_note else False
            vals = {
                'id': line.id,
                'name': line.name,
                'level': line.level,
                'columns': [{'name': l, 'class': 'number'} for l in res['line']],
                'unfoldable': len(domain_ids) > 1 and line.show_domain != 'always',
                'unfolded': line.id in options.get('unfolded_lines', []) or line.show_domain == 'always',
                'show_report_code': line.show_report_code,
                'report_code': report_code,
                'show_report_note': line.show_report_note,
                'report_note': report_note,
                'show_on_pdf': line.show_on_pdf,
            }

            if line.action_id:
                vals['action_id'] = line.action_id.id
            domain_ids.remove('line')
            lines = [vals]
            groupby = line.groupby or 'aml'
            if line.id in options.get('unfolded_lines', []) or line.show_domain == 'always':
                if line.groupby:
                    domain_ids = sorted(list(domain_ids), key=lambda k: line._get_gb_name(k))
                for domain_id in domain_ids:
                    name = line._get_gb_name(domain_id)
                    line_id = domain_id != None and line.id * 1000000 + domain_id or domain_id
                    vals = {
                        'id': line_id,
                        'line_id': line.id,
                        'account_id': domain_id,
                        'name': name and len(name) >= 45 and name[0:40] + '...' or name,
                        'level': 4,
                        'parent_id': line.id,
                        'columns': [{'name': l, 'class': 'number'} for l in res[domain_id]],
                        'caret_options': groupby == 'account_id' and 'account.account' or groupby,
                        'show_report_code': line.show_report_code,
                        'show_report_note': line.show_report_note,
                        'show_on_pdf': line.show_on_pdf,
                    }
                    if line.financial_report_id.name == 'Aged Receivable':
                        vals['trust'] = self.env['res.partner'].browse([domain_id]).trust
                    lines.append(vals)
                if domain_ids:
                    line_data = {
                        'id': 'total_' + str(line.id),
                        'name': _('Total') + ' ' + line.name,
                        'class': 'o_af_reports_domain_total',
                        'parent_id': line.id,
                        'columns': copy.deepcopy(lines[0]['columns']),
                        'show_report_code': line.show_report_code,
                        'show_report_note': line.show_report_note,
                        'show_on_pdf': line.show_on_pdf,
                    }
                    lines.append(line_data)

            for vals in lines:
                if len(comparison_table) == 2:
                    vals['columns'].append(line._build_cmp(vals['columns'][0]['name'], vals['columns'][1]['name']))
                    for i in [0, 1]:
                        vals['columns'][i] = line._format(vals['columns'][i])
                else:
                    vals['columns'] = [line._format(v) for v in vals['columns']]
                if not line.formulas:
                    vals['columns'] = [{'name': ''} for k in vals['columns']]

            if len(lines) == 1:
                new_lines = line.children_ids.get_lines(financial_report, currency_table, options, linesDicts)
                if new_lines and line.level > 0 and line.formulas:
                    if self.env.context.get('print_mode', False):
                        if financial_report.show_parent_line_first:
                            result = lines + new_lines
                        else:
                            result = new_lines + lines
                    else:
                        divided_lines = self._divide_line(lines[0], financial_report)
                        if financial_report.show_parent_line_first:
                            result = [divided_lines[1]] + new_lines
                        else:
                            result = new_lines + [divided_lines[1]]
                else:
                    result = []
                    if line.level > 0:
                        result += lines
                    result += new_lines
                    if line.level <= 0:
                        result += lines
            else:
                result = lines
            final_result_table += result
        return final_result_table

    def _divide_line(self, line, financial_report=False):
        line1 = {
            'id': line['id'],
            'name': line['name'],
            'level': line['level'],
            'columns': [{'name': ''}] * len(line['columns']),
            'unfoldable': line['unfoldable'],
            'unfolded': line['unfolded'],
            'show_report_code': line['show_report_code'],
            'show_report_note': line['show_report_note'],
            'show_on_pdf': line['show_on_pdf'],
#             'report_code': line['report_code'],

        }
        line2 = {
            'id': line['id'],
            'name': _('Total') + ' ' + line['name'],
            'class': 'total',
            'level': line['level'] + 1,
            'columns': line['columns'],
            'show_report_code': line['show_report_code'],
            'report_code': line['report_code'],
            'show_report_note': line['show_report_note'],
            'report_note': line['report_note'],
            'show_on_pdf': line['show_on_pdf'],
        }
        return [line1, line2]
