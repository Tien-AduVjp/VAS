import logging
from odoo.tests.common import tagged
from odoo.addons.to_account_reports.tests.common import Common

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


@tagged('post_install', '-at_install')
class Common(Common):

    @classmethod
    def setUpClass(cls): 
        super(Common, cls).setUpClass()

        # Create accounting user.
        account_user_vn = cls.env['res.users'].create({
            'name': 'Accountant VN',
            'login': 'accountantvn',
            'groups_id': [(6, 0, cls.env.user.groups_id.ids),
                          (4, cls.env.ref('account.group_account_user').id),
                          (4, cls.env.ref('analytic.group_analytic_accounting').id)],
        })

        # Shadow the current environment/cursor with one having the report user.
        # This is mandatory to test access rights.
        cls.env = cls.env(user=account_user_vn)
        cls.cr = cls.env.cr
        
        chart_template_vn = cls.env.ref('l10n_vn.vn_template', raise_if_not_found=False)
        if not chart_template_vn:
            _logger.warn("Test skipped because there is no chart of account defined ...")
            cls.skipTest(cls, "No Chart of account found")
        
        company_data_vn = cls._setup_company_data_vn('company_vn_data', chart_template_vn)
        
        account_user_vn.write({
            'company_ids': [(6, 0, (company_data_vn['company']).ids)],
            'company_id': company_data_vn['company'].id,
        })
        
        # Default account for journal entry (exp: cls.default_account_347)
        for key, val in company_data_vn['accounts'].items():
            setattr(cls, key, val)
        
        # Default journal for journal entry
        cls.default_journal_vn_misc = company_data_vn['default_journal_misc']
        cls.default_journal_vn_sale = company_data_vn['default_journal_sale']
        cls.default_journal_vn_purchase = company_data_vn['default_journal_purchase']
        cls.default_journal_vn_bank = company_data_vn['default_journal_bank']
        cls.default_journal_vn_cash = company_data_vn['default_journal_cash']
        
        # Default tax
        cls.tax_price_vn_purchase_5 = cls.env['account.tax'].create({
            'name': '5% purchase',
            'type_tax_use': 'purchase',
            'amount_type': 'percent',
            'amount': 5,
        })
        cls.tax_repartition_line_vn_purchase_5 = cls.tax_price_vn_purchase_5.refund_repartition_line_ids.filtered(lambda line: line.repartition_type == 'tax')
            
        cls.tax_price_vn_purchase_10 = cls.env['account.tax'].create({
            'name': '10% purchase',
            'type_tax_use': 'purchase',
            'amount_type': 'percent',
            'amount': 10,
        })
        cls.tax_repartition_line_vn_purchase_10 = cls.tax_price_vn_purchase_10.refund_repartition_line_ids.filtered(lambda line: line.repartition_type == 'tax')
        
        cls.tax_price_vn_sale_5 = cls.env['account.tax'].create({
            'name': '5% sale',
            'type_tax_use': 'sale',
            'amount_type': 'percent',
            'amount': 5,
        })
        cls.tax_repartition_line_vn_sale_5 = cls.tax_price_vn_sale_5.refund_repartition_line_ids.filtered(lambda line: line.repartition_type == 'tax')
        
        cls.tax_price_vn_sale_10 = cls.env['account.tax'].create({
            'name': '10% sale',
            'type_tax_use': 'sale',
            'amount_type': 'percent',
            'amount': 10,
        })
        cls.tax_repartition_line_vn_sale_10 = cls.tax_price_vn_sale_10.refund_repartition_line_ids.filtered(lambda line: line.repartition_type == 'tax')
    
        # Account Analytic Tag
        cls.analytic_tag_short_term_prepaid_expense = cls.env.ref('l10n_vn_c200.analytic_tag_short_term_prepaid_expense')
        cls.analytic_tag_long_term_prepaid_expense = cls.env.ref('l10n_vn_c200.analytic_tag_long_term_prepaid_expense')
        cls.analytic_tag_fixed_assets = cls.env.ref('l10n_vn_c200.analytic_tag_fixed_assets')
        cls.analytic_tag_interests_dividends_distributed_profits = cls.env.ref('l10n_vn_c200.analytic_tag_interests_dividends_distributed_profits')
        cls.analytic_tag_borrowing_loan = cls.env.ref('l10n_vn_c200.analytic_tag_borrowing_loan')
        cls.analytic_tag_lending_loan = cls.env.ref('l10n_vn_c200.analytic_tag_lending_loan')
    
    @classmethod
    def _setup_company_data_vn(cls, company_name, chart_template, **kwargs):
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
            'default_journal_misc': account_journal.filtered(lambda p: p.type == 'general')[:1],
            'default_journal_sale': account_journal.filtered(lambda p: p.type == 'sale')[:1],
            'default_journal_purchase': account_journal.filtered(lambda p: p.type == 'purchase')[:1],
            'default_journal_bank': account_journal.filtered(lambda p: p.type == 'bank')[:1],
            'default_journal_cash': account_journal.filtered(lambda p: p.type == 'cash')[:1],
        }
        
        # Accounts should be added to the company's value.
        # Return exp: 'default_journal_1111': account.account(111,)
        accounts = {}
        for account in chart_account:
            key = 'default_account_' + account.code
            accounts.update({
                key: cls._filtered_account(chart_account, chart_template, [('code', '=', account.code)])
                })
        if accounts:
            company_vals.update({'accounts': accounts})
        return company_vals
    
    def _prepare_output_value(self, block_value, output_value):
        output_value = super(Common, self)._prepare_output_value(block_value, output_value)
        for vn_currency_symbol in ['đ', '₫']:
            if vn_currency_symbol in block_value:
                index = output_value.find('.')
                output_value = '%s%s%s' % (output_value[0:index], NON_BREAKING_SPACE, vn_currency_symbol)
        return output_value
