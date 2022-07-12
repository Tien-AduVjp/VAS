try:
    # try to use UniqueViolation if psycopg2's version >= 2.8
    from psycopg2 import errors
    UniqueViolation = errors.UniqueViolation
except Exception:
    import psycopg2
    UniqueViolation = psycopg2.IntegrityError

from odoo.tests import tagged
from odoo.exceptions import ValidationError
from odoo.tools import mute_logger

from .test_common import TestCommon


@tagged('post_install', '-at_install')
class TestProductWarrantyPolicy(TestCommon):
    
    def test_check_default_converted_currency_01(self):
        """
        [Functional Test] - TC01
        
        - Case: Change default converted currency of payment acquirer in case:
            + this currency is not in list of supported currency map of payment acquirer
        - Expected Result: Error occurs (ValidationError)
        """
        with self.assertRaises(ValidationError):
            self.default_payment_acquirer.write({
                'default_converted_currency_id': self.currency_vnd.id
            })
            
    def test_check_default_converted_currency_02(self):
        """
        [Functional Test] - TC02
        
        - Case: Change default converted currency of payment acquirer in case:
            +  this currency is in list of supported currency map of payment acquirer
        - Expected Result: Change success
        """
        self.default_payment_acquirer.write({
            'default_converted_currency_id': self.currency_eur.id
        })
            
    def test_check_default_converted_currency_03(self):
        """
        [Functional Test] - TC03
        
        - Case: Change default converted currency of payment acquirer in case:
            +  payment acquirer doesn't have supported currency map
        - Expected Result: Change success
        """
        self.default_payment_acquirer.supported_currency_map_ids.unlink()
       
        self.default_payment_acquirer.write({
            'default_converted_currency_id': self.currency_usd.id
        })
        
    def test_setting_supported_currency_map_01(self):
        """
        [Functional Test] - TC04
        
        - Case: Add new currencies into supported currency map of payment acquirer:
            +  there are some active currencies, some inactive currencies in this list
        - Expected Result: supported currencies of payment acquirer only contains active currency in supported currency map
        """
        self.default_payment_acquirer.write({
            'supported_currency_map_ids': [
                (0, 0, {
                    'currency_id': self.currency_vnd.id,
                }),
                (0, 0, {
                    'currency_id': self.currency_jpy.id,
                }),
                (0, 0, {
                    'currency_id': self.currency_hkd.id,
                }),
                (0, 0, {
                    'currency_id': self.currency_fkp.id,
                }),
            ]
        })
        expected_supported_currencies = self.env['res.currency']
        expected_supported_currencies |= self.currency_eur
        expected_supported_currencies |= self.currency_usd
        expected_supported_currencies |= self.currency_vnd
        expected_supported_currencies |= self.currency_jpy
        expected_supported_currencies |= self.currency_hkd
        
        self.assertTrue(self.default_payment_acquirer.supported_currency_ids == expected_supported_currencies)
    
    def test_setting_supported_currency_map_02(self):
        """
        [Functional Test] - TC05
        
        - Case: Add duplicated currency into supported currency map of payment acquirer
        - Expected Result: Error occurs (UniqueViolation)
        """
        with mute_logger('odoo.sql_db'):
            with self.assertRaises(UniqueViolation):
                self.default_payment_acquirer.write({
                    'supported_currency_map_ids': [
                        (0, 0, {
                            'currency_id': self.currency_eur.id,
                        })
                    ]
                })
            
    def test_setting_supported_currency_map_03(self):
        """
        [Functional Test] - TC06
        
        - Case: Create new currency and adding it into supported currency map of payment acquirer
        - Expected Result: supported currencies of payment acquirer has created new currency
        """
        other_currency = self.env['res.currency'].create({'name': 'other currency',
                                                          'symbol': 'other'})
        
        self.default_payment_acquirer.write({
            'supported_currency_map_ids': [
                (0, 0, {
                    'currency_id': other_currency.id,
                })
            ]
        })
        expected_supported_currencies = self.env['res.currency']
        expected_supported_currencies |= self.currency_eur
        expected_supported_currencies |= self.currency_usd
        expected_supported_currencies |= other_currency
        
        self.assertTrue(self.default_payment_acquirer.supported_currency_ids == expected_supported_currencies)
    
    def test_setting_supported_currency_map_04(self):
        """
        [Functional Test] - TC07
        
        - Case: Change a currency, which in supported currency map, from active to inactive
        - Expected Result: this currency will be removed from supported currencies of payment acquirer
        """

        self.currency_eur.active = False
        
        expected_supported_currencies = self.env['res.currency']
        expected_supported_currencies |= self.currency_usd
        
        self.assertTrue(self.default_payment_acquirer.supported_currency_ids == expected_supported_currencies)
        
    def test_setting_supported_currency_map_05(self):
        """
        [Functional Test] - TC08
        
        - Case: Remove a currency from supported currency map of payment acquirer
        - Expected Result: this currency will be removed from supported currencies of payment acquirer
        """

        currency_eur_map = self.default_payment_acquirer.supported_currency_map_ids.filtered(lambda sc: sc.currency_id == self.currency_eur)[0]
        currency_eur_map.unlink()
        
        expected_supported_currencies = self.env['res.currency']
        expected_supported_currencies |= self.currency_usd
        
        self.assertTrue(self.default_payment_acquirer.supported_currency_ids == expected_supported_currencies)
        
    def test_setting_supported_currency_map_06(self):
        """
        [Functional Test] - TC09
        
        - Case: Change a currency, which is default converted currency of payment acquirer, from active to inactive
        - Expected Result: 
            + this currency still be default converted currenct of payment acquirer, 
            + but will be removed from supported currencies of payment acquirer
        """

        self.currency_usd.active = False
        expected_supported_currencies = self.env['res.currency']
        expected_supported_currencies |= self.currency_eur
        
        self.assertTrue(self.default_payment_acquirer.supported_currency_ids == expected_supported_currencies)
        self.assertTrue(self.default_payment_acquirer.default_converted_currency_id == self.currency_usd)
        
    def test_setting_supported_currency_map_07(self):
        """
        [Functional Test] - TC10
        
        - Case: Remove a currency from supported currency map of payment acquirer in case:
            + this currency is default converted currency of payment acquirer
        - Expected Result: Error occurs (ValidationError)
        """
        currency_usd_map = self.default_payment_acquirer.supported_currency_map_ids.filtered(lambda sc: sc.currency_id == self.currency_usd)[0]
        with self.assertRaises(ValidationError):
            self.default_payment_acquirer.write({
                'supported_currency_map_ids': [
                    (2, currency_usd_map.id, 0)
                ]
            })

    def test_after_install_module_01(self):
        """
        [Functional Test] - TC11
        
        - Case: Check new account journal is created for currency conversion difference after installing module
        - Expected Result: Companies, which has setting chart of template will has new account journal for currency conversion difference
        """
        companies = self.env['res.company'].search([('chart_template_id', '!=', False)])
        company_has_diff_journal = companies.filtered(lambda company: company.currency_conversion_diff_journal_id)
        self.assertTrue(companies == company_has_diff_journal)
