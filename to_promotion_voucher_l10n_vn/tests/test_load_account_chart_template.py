import logging
from odoo.tests.common import SavepointCase, tagged

_logger = logging.getLogger(__name__)


@tagged('post_install', '-at_install')
class TestAccountChartTemplate(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestAccountChartTemplate, cls).setUpClass()
        cls.company_test = cls.env['res.company'].create({'name': 'Company Test'})
        cls.env.user.company_ids |= cls.company_test
        cls.env.user.write({'company_id': cls.company_test.id})
        chart_template_vn = cls.env.ref('l10n_vn.vn_template', raise_if_not_found=False)
        if not chart_template_vn:
            _logger.warning("Test skipped because VN Chart template not found ...")
            cls.skipTest(cls, "VN Chart template not found")
        chart_template_vn.try_loading(company=cls.company_test)
        cls.account_711 = cls.env['account.account'].search([('code', '=', '711'), ('company_id', '=', cls.company_test.id)], limit=1)
        cls.account_5211 = cls.env['account.account'].search([('code', '=', '5211'), ('company_id', '=', cls.company_test.id)], limit=1)
        cls.account_3387 = cls.env['account.account'].search([('code', '=', '3387'), ('company_id', '=', cls.company_test.id)], limit=1)

    def test_load_account_chart_tenplate(self):
        self.assertRecordValues(self.company_test,
            [
                {
                    'property_promotion_voucher_profit_account_id': self.account_711.id,
                    'property_promotion_voucher_loss_account_id': self.account_5211.id,
                    'property_unearn_revenue_account_id': self.account_3387.id,
                }
            ]

        )
