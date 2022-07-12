import logging
from odoo.tests.common import tagged, SavepointCase

_logger = logging.getLogger(__name__)

@tagged('-at_install', 'post_install')
class TestVatCounterpartVn(SavepointCase):

    @classmethod
    def setUpClass(cls): 
        super(TestVatCounterpartVn, cls).setUpClass()
        cls.chart_template_vn = cls.env.ref('l10n_vn.vn_template', raise_if_not_found=False)
        if not cls.chart_template_vn:
            _logger.warn("Test skipped because there is no chart of account defined ...")
            cls.skipTest(cls, "No Chart of account found")

        cls.company_a = cls.env['res.company'].create({
            'name': 'Company A',
        })

        cls.chart_template_vn.try_loading(company=cls.company_a)

    def test_check_tax_groups_and_taxes_01(self):
        """
        [Functional Test] - TC01
        Case: Check tax groups and company's taxes after load VN chart template for this company
        Expected Result:
            + tax groups, which is VAT will have VAT counterpart account
            + taxes, which is VAT will have VAT counterpart account in their tax lines
        """

        vat_tax_groups = self.env['account.tax.group'].search([('is_vat', '=', True)])
        self.assertTrue(len(vat_tax_groups) > 0)
        self.assertTrue(len(vat_tax_groups.vat_ctp_account_id) > 0)
        accounts = vat_tax_groups.vat_ctp_account_id.mapped('code')
        accounts_1331 = [account for account in accounts if '1331' in account]
        self.assertTrue(len(accounts) == len(accounts_1331))
        
        vat_taxes = self.env['account.tax'].search([('is_vat', '=', True), 
                                                    ('tax_group_id.vat_ctp_account_id', '!=', False),
                                                    ('company_id', '=', self.company_a.id)])
        self.assertTrue(len(vat_taxes.invoice_repartition_line_ids.vat_ctp_account_id) > 0)
        accounts = vat_taxes.invoice_repartition_line_ids.vat_ctp_account_id.mapped('code')
        accounts_1331 = [account for account in accounts if '1331' in account]
        self.assertTrue(len(accounts) == len(accounts_1331))
        
        self.assertTrue(len(vat_taxes.invoice_repartition_line_ids.vat_ctp_account_id) > 0)
        accounts = vat_taxes.refund_repartition_line_ids.vat_ctp_account_id.mapped('code')
        accounts_1331 = [account for account in accounts if '1331' in account]
        self.assertTrue(len(accounts) == len(accounts_1331))
