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
        
        self.contact_b = self.env['res.partner'].with_context(tracking_disable=True).create({
            'name':'Contact B',
            'company_type': 'person',
            'phone': '',
            'mobile': ''
        })
        
        self.contact_c = self.env['res.partner'].with_context(tracking_disable=True).create({
            'name':'Contact B',
            'company_type': 'person',
            'phone': '-',
            'mobile': '-'
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
        list_partner = self.env['res.partner'].search_read(['|', '|', '|', '|', ('phone', 'ilike', search_operand),
                                                            ('mobile', 'ilike', search_operand),
                                                            ('phone_no_format', 'ilike', search_operand),
                                                            ('mobile_no_format', 'ilike', search_operand),
                                                            ('name', 'ilike', search_operand)], ['id'])
        self.assertIn({'id': self.contact_a.id}, list_partner)

        search_operand = self.contact_a.name
        list_partner = self.env['res.partner'].search_read(['|', '|', '|', '|', ('phone', 'ilike', search_operand),
                                                            ('mobile', 'ilike', search_operand),
                                                            ('phone_no_format', 'ilike', search_operand),
                                                            ('mobile_no_format', 'ilike', search_operand),
                                                            ('name', 'ilike', search_operand)], ['id'])
        self.assertIn({'id': self.contact_a.id}, list_partner)
    
    def test_08_filter_partner_by_phone(self):
        search_operand = '0'
        list_partner = self.env['res.partner'].search_read([('phone', 'not ilike', search_operand)], ['id'])
        self.assertIn({'id': self.contact_a.id}, list_partner)
        
    def test_09_filter_partner_by_phone(self):
        search_operand = '+84 912.345-234'
        list_partner = self.env['res.partner'].search_read([('phone', '=', search_operand)], ['id'])
        self.assertIn({'id': self.contact_a.id}, list_partner)
        
    def test_10_filter_partner_by_phone(self):
        search_operand = '345-234'
        list_partner = self.env['res.partner'].search_read([('phone', '!=', search_operand)], ['id'])
        self.assertIn({'id': self.contact_a.id}, list_partner)
        
    def test_11_filter_partner_by_phone(self):
        search_operand = ''
        list_partner = self.env['res.partner'].search_read([('phone', '=', search_operand)], ['id'])
        self.assertIn({'id': self.contact_b.id}, list_partner)
        
    def test_12_filter_partner_by_phone(self):
        search_operand = ''
        list_partner = self.env['res.partner'].search_read([('phone', '!=', search_operand)], ['id'])
        self.assertIn({'id': self.contact_a.id}, list_partner)
    
    def test_14_filter_partner_by_mobile(self):
        search_operand = '6'
        list_partner = self.env['res.partner'].search_read([('mobile', 'not ilike', search_operand)], ['id'])
        self.assertIn({'id': self.contact_a.id}, list_partner)
        
    def test_15_filter_partner_by_mobile(self):
        search_operand = '(097)-587.3421'
        list_partner = self.env['res.partner'].search_read([('mobile', '=', search_operand)], ['id'])
        self.assertIn({'id': self.contact_a.id}, list_partner)
        
    def test_16_filter_partner_by_mobile(self):
        search_operand = '345-234'
        list_partner = self.env['res.partner'].search_read([('mobile', '!=', search_operand)], ['id'])
        self.assertIn({'id': self.contact_a.id}, list_partner)
        
    def test_17_filter_partner_by_mobile(self):
        search_operand = ''
        list_partner = self.env['res.partner'].search_read([('mobile', '=', search_operand)], ['id'])
        self.assertIn({'id': self.contact_b.id}, list_partner)
        
    def test_18_filter_partner_by_mobile(self):
        search_operand = ''
        list_partner = self.env['res.partner'].search_read([('mobile', '!=', search_operand)], ['id'])
        self.assertIn({'id': self.contact_a.id}, list_partner)
    
    def test_20_filter_partner_by_phone_and_mobile(self):
        search_operand = '6'
        list_partner = self.env['res.partner'].search_read(['|', ('mobile', 'not ilike', search_operand), ('phone', 'not ilike', search_operand)], ['id'])
        self.assertIn({'id': self.contact_a.id}, list_partner)
        
    def test_21_filter_partner_by_phone_and_mobile(self):
        search_operand = '(097)-587.3421'
        list_partner = self.env['res.partner'].search_read(['|', ('mobile', '=', search_operand), ('phone', '=', search_operand)], ['id'])
        self.assertIn({'id': self.contact_a.id}, list_partner)
        
    def test_22_filter_partner_by_phone_and_mobile(self):
        search_operand = '345-234'
        list_partner = self.env['res.partner'].search_read(['|', ('mobile', '!=', search_operand), ('phone', '!=', search_operand)], ['id'])
        self.assertIn({'id': self.contact_a.id}, list_partner)
        
    def test_23_filter_partner_by_phone_and_mobile(self):
        search_operand = ''
        list_partner = self.env['res.partner'].search_read(['|', ('mobile', '=', search_operand), ('phone', '=', search_operand)], ['id'])
        self.assertIn({'id': self.contact_b.id}, list_partner)
        
    def test_24_filter_partner_by_phone_and_mobile(self):
        search_operand = ''
        list_partner = self.env['res.partner'].search_read(['|', ('mobile', '!=', search_operand), ('phone', '!=', search_operand)], ['id'])
        self.assertIn({'id': self.contact_a.id}, list_partner)
      
    def test_25_filter_partner_by_phone_and_mobile(self):
        list_partner = self.env['res.partner'].search_read(['|', '|', '|', '|', '|', '|', '|', '|', '|', '|', '|',
                                                            ('mobile', 'ilike', '*'),
                                                            ('phone', 'ilike', '*'),
                                                            ('mobile', 'ilike', ','),
                                                            ('phone', 'ilike', ','),
                                                            ('mobile', 'ilike', '.'),
                                                            ('phone', 'ilike', '.'),
                                                            ('mobile', 'ilike', '('),
                                                            ('phone', 'ilike', '('),
                                                            ('mobile', 'ilike', ')'),
                                                            ('phone', 'ilike', ')'),
                                                            ('mobile', 'ilike', '-'),
                                                            ('phone', 'ilike', '-')], ['id'])
        self.assertIn({'id': self.contact_a.id}, list_partner)
    
    def test_26_filter_partner_by_phone_and_mobile(self):
        list_partner = self.env['res.partner'].search_read(['|', '|', '|', '|', '|', '|', '|', '|', '|', '|', '|',
                                                            ('mobile', 'not ilike', '*'),
                                                            ('phone', 'not ilike', '*'),
                                                            ('mobile', 'not ilike', ','),
                                                            ('phone', 'not ilike', ','),
                                                            ('mobile', 'not ilike', '.'),
                                                            ('phone', 'not ilike', '.'),
                                                            ('mobile', 'not ilike', '('),
                                                            ('phone', 'not ilike', '('),
                                                            ('mobile', 'not ilike', ')'),
                                                            ('phone', 'not ilike', ')'),
                                                            ('mobile', 'not ilike', '-'),
                                                            ('phone', 'not ilike', '-')], ['id'])
        self.assertIn({'id': self.contact_b.id}, list_partner)
        
    def test_27_filter_partner_by_phone(self):
        list_partner = self.env['res.partner'].search_read(['|', '|', '|', '|', '|',
                                                            ('phone', 'ilike', '*'),
                                                            ('phone', 'ilike', '-'),
                                                            ('phone', 'ilike', ','),
                                                            ('phone', 'ilike', '.'),
                                                            ('phone', 'ilike', '('),
                                                            ('phone', 'ilike', ')')], ['id'])
        self.assertIn({'id': self.contact_a.id}, list_partner)
        
    def test_28_filter_partner_by_phone(self):
        list_partner = self.env['res.partner'].search_read(['|', '|', '|', '|', '|',
                                                            ('phone', 'not ilike', '*'),
                                                            ('phone', 'not ilike', '-'),
                                                            ('phone', 'not ilike', ','),
                                                            ('phone', 'not ilike', '.'),
                                                            ('phone', 'not ilike', '('),
                                                            ('phone', 'not ilike', ')')], ['id'])
        self.assertIn({'id': self.contact_b.id}, list_partner)
        
    def test_29_filter_partner_by_mobile(self):
        list_partner = self.env['res.partner'].search_read(['|', '|', '|', '|', '|',
                                                            ('mobile', 'ilike', '*'),
                                                            ('mobile', 'ilike', '-'),
                                                            ('mobile', 'ilike', ','),
                                                            ('mobile', 'ilike', '.'),
                                                            ('mobile', 'ilike', '('),
                                                            ('mobile', 'ilike', ')')], ['id'])
        self.assertIn({'id': self.contact_a.id}, list_partner)
        
    def test_30_filter_partner_by_mobile(self):
        list_partner = self.env['res.partner'].search_read(['|', '|', '|', '|', '|',
                                                            ('mobile', 'not ilike', '*'),
                                                            ('mobile', 'not ilike', '-'),
                                                            ('mobile', 'not ilike', ','),
                                                            ('mobile', 'not ilike', '.'),
                                                            ('mobile', 'not ilike', '('),
                                                            ('mobile', 'not ilike', ')')], ['id'])
        self.assertIn({'id': self.contact_b.id}, list_partner)
    
    def test_31_filter_partner_by_phone_and_mobile(self):
        list_partner = self.env['res.partner'].search_read(['|', '|', '|', '|', '|', '|', '|', '|', '|', '|', '|',
                                                            ('mobile', '=', '*'),
                                                            ('phone', '=', '*'),
                                                            ('mobile', '=', ','),
                                                            ('phone', '=', ','),
                                                            ('mobile', '=', '.'),
                                                            ('phone', '=', '.'),
                                                            ('mobile', '=', '('),
                                                            ('phone', '=', '('),
                                                            ('mobile', '=', ')'),
                                                            ('phone', '=', ')'),
                                                            ('mobile', '=', '-'),
                                                            ('phone', '=', '-')], ['id'])
        self.assertIn({'id': self.contact_c.id}, list_partner)
    
    def test_32_filter_partner_by_phone_and_mobile(self):
        list_partner = self.env['res.partner'].search_read(['|', '|', '|', '|', '|', '|', '|', '|', '|', '|', '|',
                                                            ('mobile', '!=', '*'),
                                                            ('phone', '!=', '*'),
                                                            ('mobile', '!=', ','),
                                                            ('phone', '!=', ','),
                                                            ('mobile', '!=', '.'),
                                                            ('phone', '!=', '.'),
                                                            ('mobile', '!=', '('),
                                                            ('phone', '!=', '('),
                                                            ('mobile', '!=', ')'),
                                                            ('phone', '!=', ')'),
                                                            ('mobile', '!=', '-'),
                                                            ('phone', '!=', '-')], ['id'])
        self.assertIn({'id': self.contact_a.id}, list_partner)
        
    def test_33_filter_partner_by_phone(self):
        list_partner = self.env['res.partner'].search_read(['|', '|', '|', '|', '|',
                                                            ('phone', '=', '*'),
                                                            ('phone', '=', ','),
                                                            ('phone', '=', '.'),
                                                            ('phone', '=', '('),
                                                            ('phone', '=', ')'),
                                                            ('phone', '=', '-')], ['id'])
        self.assertIn({'id': self.contact_c.id}, list_partner)
        
    def test_34_filter_partner_by_phone(self):
        list_partner = self.env['res.partner'].search_read(['|', '|', '|', '|', '|',
                                                            ('phone', '!=', '*'),
                                                            ('phone', '!=', ','),
                                                            ('phone', '!=', '.'),
                                                            ('phone', '!=', '('),
                                                            ('phone', '!=', ')'),
                                                            ('phone', '=', '-')], ['id'])
        self.assertIn({'id': self.contact_a.id}, list_partner)
        
    def test_35_filter_partner_by_mobile(self):
        list_partner = self.env['res.partner'].search_read(['|', '|', '|', '|', '|',
                                                            ('mobile', '=', '*'),
                                                            ('mobile', '=', ','),
                                                            ('mobile', '=', '.'),
                                                            ('mobile', '=', '('),
                                                            ('mobile', '=', ')'),
                                                            ('mobile', '=', '-')], ['id'])
        self.assertIn({'id': self.contact_c.id}, list_partner)
        
    def test_36_filter_partner_by_mobile(self):
        list_partner = self.env['res.partner'].search_read(['|', '|', '|', '|', '|',
                                                            ('mobile', '!=', '*'),
                                                            ('mobile', '!=', ','),
                                                            ('mobile', '!=', '.'),
                                                            ('mobile', '!=', '('),
                                                            ('mobile', '=', '-'),
                                                            ('mobile', '!=', ')')], ['id'])
        self.assertIn({'id': self.contact_a.id}, list_partner)
