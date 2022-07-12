from odoo.tests.common import TransactionCase, tagged


@tagged('post_install', '-at_install')
class TestFilterPartnerByPhone(TransactionCase):
    
    def setUp(self):
        super(TestFilterPartnerByPhone, self).setUp()
        
        self.contact_a = self.env['res.partner'].with_context(tracking_disable=True).create({
            'name':'Contact A',
            'company_type': 'person',
            'phone': '+84 912.345-234',
            'mobile': '(097)-587.3421'
        })
    
    def test_01_filter_partner_by_phone(self):
        search_operand = '0912345234'
        list_partner = self.env['res.partner'].search_read(['|', '|', '|', ('phone', 'ilike', search_operand),
                                                            ('mobile', 'ilike', search_operand), 
                                                            ('phone_no_format', 'ilike', search_operand), 
                                                            ('mobile_no_format', 'ilike', search_operand)], ['id'])               
        self.assertIn({'id': self.contact_a.id}, list_partner)
        
        
    def test_02_filter_partner_by_phone(self):
        search_operand = '+84912345234'
        list_partner = self.env['res.partner'].search_read(['|', '|', '|', ('phone', 'ilike', search_operand),
                                                            ('mobile', 'ilike', search_operand), 
                                                            ('phone_no_format', 'ilike', search_operand), 
                                                            ('mobile_no_format', 'ilike', search_operand)], ['id'])               
        self.assertIn({'id': self.contact_a.id}, list_partner)
        
    def test_03_filter_partner_by_phone(self):
        search_operand = '1234'
        list_partner = self.env['res.partner'].search_read(['|', '|', '|', ('phone', 'ilike', search_operand),
                                                            ('mobile', 'ilike', search_operand), 
                                                            ('phone_no_format', 'ilike', search_operand), 
                                                            ('mobile_no_format', 'ilike', search_operand)], ['id'])               
        self.assertIn({'id': self.contact_a.id}, list_partner)
        
    def test_04_filter_partner_by_phone(self):
        search_operand = '97-58'
        list_partner = self.env['res.partner'].search_read(['|', '|', '|', ('phone', 'ilike', search_operand),
                                                            ('mobile', 'ilike', search_operand), 
                                                            ('phone_no_format', 'ilike', search_operand), 
                                                            ('mobile_no_format', 'ilike', search_operand)], ['id'])               
        self.assertIn({'id': self.contact_a.id}, list_partner)

    def test_05_filter_partner_by_phone(self):
        search_operand = '7)-587.3'
        list_partner = self.env['res.partner'].search_read(['|', '|', '|', ('phone', 'ilike', search_operand),
                                                            ('mobile', 'ilike', search_operand), 
                                                            ('phone_no_format', 'ilike', search_operand), 
                                                            ('mobile_no_format', 'ilike', search_operand)], ['id'])               
        self.assertIn({'id': self.contact_a.id}, list_partner)

    def test_06_filter_partner_by_phone(self):
        search_operand = '(097)-587.3421'
        list_partner = self.env['res.partner'].search_read(['|', '|', '|', ('phone', 'ilike', search_operand),
                                                            ('mobile', 'ilike', search_operand), 
                                                            ('phone_no_format', 'ilike', search_operand), 
                                                            ('mobile_no_format', 'ilike', search_operand)], ['id'])               
        self.assertIn({'id': self.contact_a.id}, list_partner)
    
    def test_06_filter_partner_by_phone_and_name(self):
        search_operand = '(097)-587.3421'
        list_partner = self.env['res.partner'].search_read(['|', '|', '|', '|',('phone', 'ilike', search_operand),
                                                            ('mobile', 'ilike', search_operand), 
                                                            ('phone_no_format', 'ilike', search_operand), 
                                                            ('mobile_no_format', 'ilike', search_operand),
                                                            ('name', 'ilike', search_operand)], ['id'])               
        self.assertIn({'id': self.contact_a.id}, list_partner)
        
        search_operand = self.contact_a.name
        list_partner = self.env['res.partner'].search_read(['|', '|', '|', '|',('phone', 'ilike', search_operand),
                                                            ('mobile', 'ilike', search_operand), 
                                                            ('phone_no_format', 'ilike', search_operand), 
                                                            ('mobile_no_format', 'ilike', search_operand),
                                                            ('name', 'ilike', search_operand)], ['id'])               
        self.assertIn({'id': self.contact_a.id}, list_partner)
