from odoo import _
from odoo.tests import tagged
from odoo.exceptions import UserError

from . import common


@tagged('post_install','-at_install')
class TestInterCompanySalePurchase(common.Common):
   
    def test_01_auto_generate_validated_sale_order(self):
        """
            When create a PO to vendor is an inter-company with so_po_auto_validation is validated,
            a validated SO will be auto generated in that company.
        """
        self.vendor_company.update({
            'so_po_auto_validation':'validated'
        })
        self.purchase_order.button_confirm()
        inter_company_sale_order = self.env['sale.order'].search(
            [
                ('company_id','=',self.vendor_company.id),
                ('inter_comp_purchase_order_id','=',self.purchase_order.id)
            ])
        self.assertTrue(len(inter_company_sale_order) == 1 and inter_company_sale_order.state == 'sale',
        "Validated sale order of Vendor Company should be created correlative with purchase order of Customer Company")        
        #Test message log is created in SO when PO is canceled.
        self.purchase_order.button_cancel()
        message = _("The inter-company invoice %s of the company %s was cancelled. Please contact that company to solve the issue.")\
                % (self.purchase_order.name, self.purchase_order.company_id.name)        
        self.assertTrue(inter_company_sale_order.message_ids.filtered(lambda m:message in m.body) and True,
        "Message log should be create in SO when PO was canceled")

    def test_02_auto_generate_validated_purchase_order(self):
        """
            When create a SO to customer is an inter-company with so_po_auto_validation is validated,
            a validated PO will be auto generated in that company.
        """
        self.customer_company.update({
            'so_po_auto_validation':'validated'
        })
        self.sale_order.action_confirm()
        inter_company_purchase_order = self.env['purchase.order'].search(
            [
                ('company_id','=',self.customer_company.id),
                ('inter_comp_sale_order_id','=',self.sale_order.id)
            ])     
        self.assertTrue(len(inter_company_purchase_order) == 1 and inter_company_purchase_order.state == 'purchase',
        "Validated purchase order of Customer Company should be created correlative with sale order of Vendor Company")      
    
    def test_03_auto_generate_draft_sale_order(self):
        """
            When create a PO to vendor is an inter-company with so_po_auto_validation is draft,
            a draft SO will be auto generated in that company.
        """
        self.customer_company.update({
            'so_po_auto_validation':'draft'
        })
        self.purchase_order.button_confirm()
        inter_company_sale_order = self.env['sale.order'].search(
            [
                ('company_id','=',self.vendor_company.id),
                ('inter_comp_purchase_order_id','=',self.purchase_order.id)
            ])
        self.assertTrue(len(inter_company_sale_order) == 1 and inter_company_sale_order.state == 'draft',
        "Draft sale order of Vendor Company should be created correlative with purchase order of Customer Company") 

    def test_04_auto_generate_draft_purchase_order(self):
        """
            When create a SO to customer is an inter-company with so_po_auto_validation is draft,
            a draft PO will be auto generated in that company.
        """
        self.customer_company.update({
            'so_po_auto_validation':'draft'
        })
        self.sale_order.action_confirm()
        inter_company_purchase_order = self.env['purchase.order'].search(
            [
                ('company_id','=',self.customer_company.id),
                ('inter_comp_sale_order_id','=',self.sale_order.id)
            ])       
        self.assertTrue(len(inter_company_purchase_order) == 1 and inter_company_purchase_order.state == 'draft',
        "Validated purchase order of Customer Company should be created correlative with sale order of Vendor Company") 

    def test_06_prevent_generate_so_difference_currency(self):
        """
            when create PO to vendor is an inter-company with currency of PO difference currency of SO pricelist set in partner company,
            raise UserError.
        """
        customer_price_list = self.env['product.pricelist'].create({
            'name':'Default Price List EUR',
            'currency_id':self.ref('base.EUR')
        })
        self.customer_company.partner_id.with_user(self.sale_manager).update({
            'property_product_pricelist':customer_price_list.id
        })       
        with self.assertRaises(UserError):
            self.purchase_order.with_user(self.purchase_manager).button_confirm()
