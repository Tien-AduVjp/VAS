from odoo.tests import Form, tagged

from .common import TestCommon

@tagged('post_install', '-at_install')
class TestPartner(TestCommon):
    
    def test_create_partner_01(self):
        """
        [Form Test] - TC01
        
        - Case: Create partner, which has country differ from country of current company
        - Expected Result:
            + partner will be set as foreign trade partner
            + customer location of partner will be foreign customer location
        """
        with Form(self.env['res.partner']) as f:
            f.name = 'Test Partner'
            f.country_id = self.env.ref('base.vn')
            self.assertTrue(f.property_foreign_trade_partner)
            self.assertEqual(f.property_stock_customer, self.env.ref('to_foreign_trade.to_stock_location_customers_export'))
    
    def test_create_partner_02(self):
        """
        [Form Test] - TC02
        
        - Case: Create partner, which has same country with country of current company
        - Expected Result:
            + partner will not be set as foreign trade partner
            + customer location of partner will be customer location
        """
        with Form(self.env['res.partner']) as f:
            f.name = 'Test Partner'
            f.country_id = self.env.ref('base.us')
            self.assertTrue(not f.property_foreign_trade_partner)
            self.assertEqual(f.property_stock_customer, self.env.ref('stock.stock_location_customers'))
            
    def test_create_partner_03(self):
        """
        [Form Test] - TC03
        
        - Case: Create partner, which has country differ from country of selected company
        - Expected Result:
            + partner will be set as foreign trade partner
            + customer location of partner will be foreign customer location
        """
        with Form(self.env['res.partner']) as f:
            f.name = 'Test Partner'
            f.country_id = self.env.ref('base.vn')
            f.company_id = self.env.company
            self.assertTrue(f.property_foreign_trade_partner)
            self.assertEqual(f.property_stock_customer, self.env.ref('to_foreign_trade.to_stock_location_customers_export'))
            
    def test_create_partner_04(self):
        """
        [Form Test] - TC04
        
        - Case: Create partner, which has same country with country of selected company
        - Expected Result:
            + partner will not be set as foreign trade partner
            + customer location of partner will be customer location
        """
        with Form(self.env['res.partner']) as f:
            f.name = 'Test Partner'
            f.country_id = self.env.ref('base.us')
            f.company_id = self.env.company
            self.assertTrue(not f.property_foreign_trade_partner)
            self.assertEqual(f.property_stock_customer, self.env.ref('stock.stock_location_customers'))
    
    
    def test_create_partner_05(self):
        """
        [Form Test] - TC05
        
        - Case: Remove country of partner, which already marked as foreign trade partner
        - Expected Result:
            + partner will still be set as foreign trade partner
            + customer location of partner will still be foreign customer location
        """
        with Form(self.env['res.partner']) as f:
            f.name = 'Test Partner'
            f.country_id = self.env.ref('base.vn')
            f.company_id = self.env.company
            self.assertTrue(f.property_foreign_trade_partner)
            self.assertEqual(f.property_stock_customer, self.env.ref('to_foreign_trade.to_stock_location_customers_export'))
        
        partner = f.save()
        
        with Form(partner) as f:
            f.country_id = self.env['res.country']
            self.assertTrue(f.property_foreign_trade_partner)
            self.assertEqual(f.property_stock_customer, self.env.ref('to_foreign_trade.to_stock_location_customers_export'))
        
    def test_create_partner_06(self):
        """
        [Form Test] - TC06
        
        - Case: Remove country of partner, which was not marked as foreign trade partner
        - Expected Result:
            + partner will still not be set as foreign trade partner
            + customer location of partner will still be customer location
        """
        with Form(self.env['res.partner']) as f:
            f.name = 'Test Partner'
            f.country_id = self.env.ref('base.us')
            f.company_id = self.env.company
            self.assertTrue(not f.property_foreign_trade_partner)
            self.assertEqual(f.property_stock_customer, self.env.ref('stock.stock_location_customers'))
            
        partner = f.save()
        with Form(partner) as f:
            f.country_id = self.env['res.country']
            self.assertTrue(not f.property_foreign_trade_partner)
            self.assertEqual(f.property_stock_customer, self.env.ref('stock.stock_location_customers'))
            
    def test_create_partner_07(self):
        """
        [Functional Test] - TC08
        
        - Case: Create new partner in which has country differ from country of company 
        - Expected Result:
            + partner will be marked as foreign trade partner
            + customer location of partner will be set as foreign customer location
        """
        new_partner = self.env['res.partner'].create({
            'name': 'Test New Foreign Partner',
            'email': 'vn1.partner@example.viindoo.com',
            'country_id': self.env.ref('base.vn').id,
            'company_id': self.env.company.id
        })
        self.assertTrue(new_partner.property_foreign_trade_partner)
        self.assertEqual(new_partner.property_stock_customer, self.env.ref('to_foreign_trade.to_stock_location_customers_export'))
    
    def test_create_partner_08(self):
        """
        [Functional Test] - TC09
        
        - Case: update partner in which has country differ from country of company 
        - Expected Result:
            + partner will be marked as foreign trade partner
            + customer location of partner will be set as foreign customer location
        """
        new_partner = self.env['res.partner'].create({
            'name': 'Test New Foreign Partner',
            'email': 'vn1.partner@example.viindoo.com',
            'country_id': self.env.ref('base.us').id,
            
        })
        self.assertTrue(not new_partner.property_foreign_trade_partner)
        self.assertEqual(new_partner.property_stock_customer, self.env.ref('stock.stock_location_customers'))
        
        new_partner.write({
            'country_id': self.env.ref('base.vn').id,
            'company_id': self.env.company.id
        })
        self.assertTrue(new_partner.property_foreign_trade_partner)
        self.assertEqual(new_partner.property_stock_customer, self.env.ref('to_foreign_trade.to_stock_location_customers_export'))
