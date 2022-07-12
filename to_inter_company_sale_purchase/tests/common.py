from odoo import fields, _
from odoo.tests import TransactionCase


class Common(TransactionCase):
    def setUp(self):
        super(Common, self).setUp()
        self.vendor_company = self.env['res.company'].create({
            'name':'Vendor Company',
            'currency_id':self.ref('base.USD'),
            'applicable_on':'purchase'         
        })
        self.customer_company = self.env['res.company'].create({
            'name':'Customer Company',
            'currency_id':self.ref('base.USD'),
            'applicable_on':'sale'           
        })
        self.purchase_manager = self.env['res.users'].create({
            'name':'Viin Purchase Manager',
            'email':'viin.purchase_manager@vendor_company.com',
            'login':'purchase_manager_test_01',
            'company_id':self.customer_company.id,
            'company_ids':[(6,0, [self.customer_company.id])],
            'groups_id':[(6, 0,[self.ref('purchase.group_purchase_manager')])]             
        })
        self.sale_manager = self.env['res.users'].create({
            'name':'Viin Sale Manager',
            'email':'viin.sale_manager@customer_company.com',
            'login':'sale_manager_test_01',
            'company_id':self.vendor_company.id,
            'company_ids':[(6,0, [self.vendor_company.id])],
            'groups_id':[(6, 0,[self.ref('sales_team.group_sale_manager')])]              
        })  
        self.product_test_01 = self.env['product.product'].with_user(self.sale_manager).create({
            'name':'Viin Product Test 01',
            'type':'product'            
        })
        self.product_test_02 = self.env['product.product'].with_user(self.purchase_manager).create({
            'name':'Viin Product Test 01',
            'type':'product'          
        })
        self.purchase_order = self.env['purchase.order'].with_user(self.purchase_manager).create({            
            'partner_id':self.vendor_company.partner_id.id,     
            'order_line':[(0,0,{
                'name':'Purchase Order Line',
                'product_id':self.product_test_02.id,
                'product_qty':1,
                'price_unit':100.0,
                'product_uom':self.ref('uom.product_uom_unit'), 
                'date_planned':fields.date.today()
            })]
        })     
        self.sale_order = self.env['sale.order'].with_user(self.sale_manager).create({        
            'partner_id':self.customer_company.partner_id.id,         
            'order_line':[(0,0,{               
                'product_id':self.product_test_01.id,              
                'product_uom_qty':1,
                'price_unit':100.0              
            })]
        })
