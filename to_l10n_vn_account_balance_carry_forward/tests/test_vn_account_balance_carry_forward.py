import logging
from odoo.tests.common import tagged, SavepointCase

_logger = logging.getLogger(__name__)


@tagged('post_install', '-at_install')
class TestVnAccountBalanceCarryForward(SavepointCase):
    
    
    def setUp(self): 
        super(TestVnAccountBalanceCarryForward, self).setUp()
        self.company_test = self.env['res.company'].create({
            'name': 'Company Test',
        })
        self.env.user.company_ids |= self.company_test
        
    def test_01_vn_chart_template(self):
        chart_template_vn = self.env.ref('l10n_vn.vn_template', raise_if_not_found=False)
        if not chart_template_vn:
            _logger.warn("Test skipped because VN Chart template not found ...")
            self.skipTest("VN Chart template not found")
            
        chart_template_vn.try_loading(company=self.company_test)
        balance_carry_forward_rules = self.env['balance.carry.forward.rule'].search([('company_id', '=', self.company_test.id)])
        self.assertEqual(len(balance_carry_forward_rules), 16)
        
        accounts = self.env['account.account'].search([('company_id', '=', self.company_test.id)])
        account_911 = accounts.filtered_domain([('code', '=ilike', '911%')])[:1]
        account_5111 = accounts.filtered_domain([('code', '=ilike', '5111%')])[:1]
        account_521 = accounts.filtered_domain([('code', '=ilike', '521%')])[:1]
        account_4212 = accounts.filtered_domain([('code', '=ilike', '4212%')])[:1]
        
        rule_911_to_4212 = balance_carry_forward_rules.filtered(lambda r: account_911.id in r.source_account_ids.ids and \
                                                                account_4212.id == r.dest_account_id.id)[:1]
        rule_5111_to_911 = balance_carry_forward_rules.filtered(lambda r: account_5111.id in r.source_account_ids.ids and \
                                                                account_911.id == r.dest_account_id.id)[:1]
        rule_521_to_5111 = balance_carry_forward_rules.filtered(lambda r: account_521.id in r.source_account_ids.ids and \
                                                                account_5111.id == r.dest_account_id.id)[:1]
        self.assertTrue(rule_911_to_4212)
        self.assertEqual(rule_911_to_4212, rule_5111_to_911.succeeding_rule_id)
        self.assertEqual(rule_5111_to_911, rule_521_to_5111.succeeding_rule_id)
    
    def test_02_generic_chart_template(self):
        chart_template_generic = self.env.ref('l10n_generic_coa.configurable_chart_template', raise_if_not_found=False)
        if not chart_template_generic:
            _logger.warn("Test skipped because Generic Chart template not found ...")
            self.skipTest("Generic Chart template not found")
            
        chart_template_generic.try_loading(company=self.company_test)
        balance_carry_forward_rules = self.env['balance.carry.forward.rule'].search([('company_id', '=', self.company_test.id)])
        self.assertFalse(balance_carry_forward_rules)
