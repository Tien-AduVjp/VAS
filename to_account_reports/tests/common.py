import logging

from datetime import datetime
from unittest.mock import patch
from odoo import fields
from odoo.tests.common import SavepointCase

# TODO: replace try/except with the straight forward import `from odoo.tools.misc import NON_BREAKING_SPACE` in 15+
try:
    # NON_BREAKING_SPACE may not exist if the Odoo source code does not contain
    # the https://github.com/odoo/odoo/pull/90191, that applies non breaking space
    # between currency and currency symbol
    # in such the case, we could use normal space ' ' as it was
    from odoo.tools.misc import NON_BREAKING_SPACE
except ImportError:
    NON_BREAKING_SPACE = ' '

_logger = logging.getLogger(__name__)


class Common(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(Common, cls).setUpClass()
        cls.no_mailthread_features_ctx = {
            'no_reset_password': True,
            'tracking_disable': True,
        }
        cls.env = cls.env(context=dict(cls.no_mailthread_features_ctx, **cls.env.context))

        # Create accounting user.
        account_user = cls.env['res.users'].create({
            'name': 'Accountant',
            'login': 'accountant',
            'groups_id': [(6, 0, cls.env.user.groups_id.ids),
                          (4, cls.env.ref('account.group_account_manager').id),
                          (4, cls.env.ref('analytic.group_analytic_accounting').id)],
        })

        # Shadow the current environment/cursor with one having the report user.
        # This is mandatory to test access rights.
        cls.env = cls.env(user=account_user)
        cls.cr = cls.env.cr

        chart_template = cls.env.ref('l10n_generic_coa.configurable_chart_template', raise_if_not_found=False)
        if not chart_template:
            _logger.warning("Test skipped because there is no chart of account defined ...")
            cls.skipTest(cls, "No Chart of account found")

        company_data = cls._setup_company_data('company_1_data', chart_template)

        account_user.write({
            'company_ids': [(6, 0, (company_data['company']).ids)],
            'company_id': company_data['company'].id,
        })

        cls.customer_a = cls.env['res.partner'].create({
            'name': 'Customer A',
            'email': 'customera@viindoo.com',
        })

        cls.customer_b = cls.env['res.partner'].create({
            'name': 'Customer B',
            'email': 'customerb@viindoo.com',
        })

        cls.vendor_a = cls.env['res.partner'].create({
            'name': 'Vendor A',
            'email': 'vendora@viindoo.com',
        })

        cls.vendor_b = cls.env['res.partner'].create({
            'name': 'Vendor B',
            'email': 'vendorb@viindoo.com',
        })

        # Default account for journal entry
        # 400000 Product Sales
        cls.default_account_revenue = company_data['default_account_revenue']
        # 600000 Expenses
        cls.default_account_expense = company_data['default_account_expense']
        # 630000 Salary Expenses
        cls.default_account_salary_expenses = company_data['default_account_salary_expenses']
        # 110200 Stock Interim (Received)
        cls.default_account_stock = company_data['default_account_stock']
        # 110300 Stock Interim (Delivered)
        cls.default_account_stock_delivered = company_data['default_account_stock_delivered']
        # 500000 Cost of Goods Sold
        cls.default_account_type_direct_cost = company_data['default_account_type_direct_cost']
        # 121000 Account Receivable
        cls.default_account_receivable = company_data['default_account_receivable']
        # 211000 Account Payable
        cls.default_account_payable = company_data['default_account_payable']
        # 201000 Current Liabilities
        cls.default_account_current_liabilities = company_data['default_account_current_liabilities']
        # 291000 Non Current Liabilities
        cls.default_account_non_current_liabilities = company_data['default_account_non_current_liabilities']
        # 101401 Bank
        cls.default_account_liquidity = company_data['default_account_liquidity']
        # 101501 Cash
        cls.default_account_cash = company_data['default_account_cash']
        # 301000 Capital
        cls.default_account_capital = company_data['default_account_capital']
        # 441000 Foreign Exchange Gain
        cls.default_account_foreign = company_data['default_account_foreign']
        # 191000 Non-Current Assets
        cls.default_account_non_assets = company_data['default_account_non_assets']
        # 151000 Fixed Asset
        cls.default_account_fixed_assets = company_data['default_account_fixed_assets']
        # 141000 Prepayments
        cls.default_account_prepayments = company_data['default_account_prepayments']
        # 251000 Tax Received
        cls.default_account_tax_sale = company_data['default_account_tax_sale']
        # 131000 Tax Paid
        cls.default_account_tax_purchase = company_data['default_account_tax_purchase']

        # Default journal for journal entry
        cls.default_journal_misc = company_data['default_journal_misc']
        cls.default_journal_sale = company_data['default_journal_sale']
        cls.default_journal_purchase = company_data['default_journal_purchase']
        cls.default_journal_bank = company_data['default_journal_bank']
        cls.default_journal_cash = company_data['default_journal_cash']

        # Default tax
        cls.tax_price_purchase_5 = cls.env['account.tax'].create({
            'name': '5% purchase',
            'type_tax_use': 'purchase',
            'amount_type': 'percent',
            'amount': 5,
        })
        cls.tax_repartition_line_purchase_5 = cls.tax_price_purchase_5.refund_repartition_line_ids.filtered(lambda line: line.repartition_type == 'tax')

        cls.tax_price_purchase_10 = cls.env['account.tax'].create({
            'name': '10% purchase',
            'type_tax_use': 'purchase',
            'amount_type': 'percent',
            'amount': 10,
        })
        cls.tax_repartition_line_purchase_10 = cls.tax_price_purchase_10.refund_repartition_line_ids.filtered(lambda line: line.repartition_type == 'tax')

        cls.tax_price_sale_5 = cls.env['account.tax'].create({
            'name': '5% sale',
            'type_tax_use': 'sale',
            'amount_type': 'percent',
            'amount': 5,
        })
        cls.tax_repartition_line_sale_5 = cls.tax_price_sale_5.refund_repartition_line_ids.filtered(lambda line: line.repartition_type == 'tax')

        cls.tax_price_sale_10 = cls.env['account.tax'].create({
            'name': '10% sale',
            'type_tax_use': 'sale',
            'amount_type': 'percent',
            'amount': 10,
        })
        cls.tax_repartition_line_sale_10 = cls.tax_price_sale_10.refund_repartition_line_ids.filtered(lambda line: line.repartition_type == 'tax')

    def _init_journal_entry(self, partner, account_date, journal, **kwargs):
        """ Create a journal entry

        :param record partner: The partner in journal entry
        :param datetime account_date: The accounting date.
        :param record journal: The journal.
        :param dict kwargs: The journal items.
        Example:
            kwargs = {
                    'items': [{
                        'product_id': product id,
                        'account_id': account id (required),
                        'debit': debit amount,
                        'credit': credit amount,
                        'tag_ids': (6, 0, list tax id),
                        },
                        {
                        'product_id': product id,
                        'account_id': account id (required),
                        'debit': debit amount,
                        'credit': credit amount,
                        'tag_ids': (6, 0, list tax id),
                        }
                        ...............................
                        ]
                    }

        :return: A journal entry (account.move) record.
        """
        with self.patch_datetime_now(account_date), self.patch_date_today(account_date), self.patch_date_context_today(account_date):
            line_vals = []
            journal_items = kwargs.get('items', False)
            if journal_items:
                for value in journal_items:
                    line_vals.append((0, 0, value))
            val = {
                'partner_id': partner and partner.id or False,
                'date': account_date.date(),
                'journal_id': journal.id,
                'line_ids': line_vals
            }
            journal_entry = self.env['account.move'].create(val)
            journal_entry.action_post()
        return journal_entry

    @classmethod
    def _setup_company_data(cls, company_name, chart_template, **kwargs):
        """ Create a new company having the name passed as parameter.
        A chart of accounts will be installed to this company: the same as the current company one.
        The current user will get access to this company.

        :param str company_name: The name of the company.
        :param record chart_template: The chart template.
        :return: A dictionary will be returned containing all relevant accounting data for testing.
        """

        currency = chart_template.currency_id
        company = cls.env['res.company'].create({
            'name': company_name,
            'currency_id': currency.id,
            **kwargs,
        })
        cls.env.user.company_ids |= company

        # Install the company's chart template.
        chart_template.try_loading(company=company)

        # The currency could be different after the installation of the chart template.
        company.write({'currency_id': kwargs.get('currency_id', currency.id)})

        chart_account = cls.env['account.account'].search([('company_id', '=', company.id)])
        account_journal = cls.env['account.journal'].search([('company_id', '=', company.id)])

        company_vals = {
            'company': company,
            'currency': company.currency_id,
            'default_account_liquidity': cls._filtered_account(chart_account, chart_template,
                                                             [('user_type_id', '=', cls.env.ref('account.data_account_type_liquidity').id)]),
            'default_account_non_assets': cls._filtered_account(chart_account, chart_template,
                                                             [('user_type_id', '=', cls.env.ref('account.data_account_type_non_current_assets').id)]),
            'default_account_revenue': cls._filtered_account(chart_account, chart_template,
                                                             [('user_type_id', '=', cls.env.ref('account.data_account_type_revenue').id)]),
            'default_account_expense': cls._filtered_account(chart_account, chart_template,
                                                             [('user_type_id', '=', cls.env.ref('account.data_account_type_expenses').id)]),
            'default_account_fixed_assets': cls._filtered_account(chart_account, chart_template,
                                                             [('user_type_id', '=', cls.env.ref('account.data_account_type_fixed_assets').id)]),
            'default_account_current_liabilities': cls._filtered_account(chart_account, chart_template,
                                                             [('user_type_id', '=', cls.env.ref('account.data_account_type_current_liabilities').id)]),
            'default_account_non_current_liabilities': cls._filtered_account(chart_account, chart_template,
                                                             [('user_type_id', '=', cls.env.ref('account.data_account_type_non_current_liabilities').id)]),
            'default_account_prepayments': cls._filtered_account(chart_account, chart_template,
                                                             [('user_type_id', '=', cls.env.ref('account.data_account_type_prepayments').id)]),
            'default_account_type_direct_cost': cls._filtered_account(chart_account, chart_template,
                                                             [('user_type_id', '=', cls.env.ref('account.data_account_type_direct_costs').id)]),
            'default_account_stock': cls._filtered_account(chart_account, chart_template,
                                                             [('code', '=', '110200')]),
            'default_account_stock_delivered': cls._filtered_account(chart_account, chart_template,
                                                             [('code', '=', '110300')]),
            'default_account_cash': cls._filtered_account(chart_account, chart_template,
                                                             [('code', '=', '101501')]),
            'default_account_salary_expenses': cls._filtered_account(chart_account, chart_template,
                                                             [('code', '=', '630000')]),
            'default_account_capital': cls._filtered_account(chart_account, chart_template,
                                                             [('code', '=', '301000')]),
            'default_account_foreign': cls._filtered_account(chart_account, chart_template,
                                                             [('code', '=', '441000')]),
            'default_account_receivable': cls._filtered_account(chart_account, chart_template, [('user_type_id.type', '=', 'receivable')],
                                                                field_name='property_account_receivable_id'),
            'default_account_payable': cls._filtered_account(chart_account, chart_template,
                                                             [('user_type_id.type', '=', 'payable')]),
            'default_account_assets': cls._filtered_account(chart_account, chart_template,
                                                             [('user_type_id', '=', cls.env.ref('account.data_account_type_current_assets').id)]),
            'default_account_tax_sale': company.account_sale_tax_id.mapped('invoice_repartition_line_ids.account_id'),
            'default_account_tax_purchase': company.account_purchase_tax_id.mapped('invoice_repartition_line_ids.account_id'),
            'default_journal_misc': account_journal.filtered(lambda p: p.type == 'general')[:1],
            'default_journal_sale': account_journal.filtered(lambda p: p.type == 'sale')[:1],
            'default_journal_purchase': account_journal.filtered(lambda p: p.type == 'purchase')[:1],
            'default_journal_bank': account_journal.filtered(lambda p: p.type == 'bank')[:1],
            'default_journal_cash': account_journal.filtered(lambda p: p.type == 'cash')[:1],
            'default_tax_sale': company.account_sale_tax_id,
            'default_tax_purchase': company.account_purchase_tax_id,
        }
        return company_vals

    @classmethod
    def _filtered_account(cls, chart_account, chart_template, domain, **kwargs):
        field_name = kwargs.get('field_name', False)
        template_code = ''
        if field_name:
            template_code = chart_template[field_name].code
        account = None
        if template_code:
            account = chart_account.filtered_domain(domain + [('code', '=like', template_code + '%')])[:1]
        if not account:
            account = chart_account.filtered_domain(domain)[:1]
        return account

    def patch_datetime_now(self, now):
        return patch('odoo.fields.Datetime.now', return_value=now)

    def patch_date_today(self, today):
        if isinstance(today, datetime):
            today = today.date()
        return patch('odoo.fields.Date.today', return_value=today)

    def patch_date_context_today(self, today):
        if isinstance(today, datetime):
            today = today.date()
        return patch('odoo.fields.Date.context_today', return_value=today)

    def _get_lines_report(self, report, datetime, filter='today', date_from=None, date_to=None, cash_basis=False):
        """
        This method retrieves the report's rows.

        :param record report: The report object
        :param datetime datetime: Today
        :param char filter: the filter of the report ('today', 'custom', 'this_month', 'this_quarter', 'this_year', 'last_month', 'last_quarter', 'last_year')
        :param date date_from: The accounting period's start date
        :param date date_to: The accounting period's end date

        :return (list of dicts) The rows of the report
        """
        with self.patch_datetime_now(datetime), self.patch_date_today(datetime), self.patch_date_context_today(datetime):
            type(report).filter_date = {
                'filter': filter,
                'date': fields.Datetime.now(),
            }
            if filter != 'today':
                type(report).filter_date.update({
                    'date_from': '',
                    'date_to': '',
                })
                if filter == 'custom':
                    type(report).filter_date.update({
                        'date_from': date_from and date_from.strftime('%Y-%m-%d') or '',
                        'date_to': date_to and date_to.strftime('%Y-%m-%d') or ''
                    })
            options = report.get_options(None)
            if cash_basis != False:
                options['cash_basis'] = cash_basis
            # apply date and date_comparison filter
            options = report.apply_date_filter(options)
            options = report.apply_cmp_filter(options)
            context = report.set_context(options)
            lines = report.with_context(context).get_lines(options)
            return lines

    def _check_report_value(self, lines, table_value):
        """
        This method for check the rows of the report

        :param list of dict lines: The rows value of the report
        :param list of tuple table_value: Expect value
        """
        # Check the report's line count
        self.assertEqual(len(lines), len(table_value), "The number of lines reported is incorrect")
        # Check the value of each line in the report
        for line_index in range(len(lines)):
            current_line = lines[line_index]
            current_value = table_value[line_index]
            colspan = current_line.get('colspan', 0)
            for column in range(len(current_value)):
                if column == 0:
                    self.assertEqual(current_value[column], current_line.get('name', ''),
                                     "In the report line %s, the criteria name is incorrect" % (line_index + 1))
                else:
                    if column < colspan:
                        continue
                    column_val = current_line.get('columns', False)
                    line_column = column - 1
                    value_column = column
                    if len(column_val) < len(current_value) - 1:
                        line_column = column - colspan
                        value_column = line_column + colspan
                    if column_val[line_column].get('name', ''):
                        block_value = str(column_val[line_column]['name'])
                        output_value = self._prepare_output_value(block_value, current_value[value_column])
                        self.assertEqual(output_value, block_value,
                                         "In the report line %s, the value is incorrect" % (line_index + 1))

    def _prepare_output_value(self, block_value, output_value):
        if '$' in block_value:
            output_value = str('${}{:,.2f}'.format(NON_BREAKING_SPACE, output_value))
        elif '%' in block_value:
            output_value = str('{:,.1f}'.format(output_value)) + '%'
        else:
            output_value = str('{:,.1f}'.format(output_value))
        return output_value
