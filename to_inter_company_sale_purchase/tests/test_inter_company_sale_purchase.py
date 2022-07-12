from odoo import _, fields
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
        #Check quantity, tax, price_unit
        self.assertTrue(inter_company_sale_order.order_line[0].price_unit == self.purchase_order.order_line[0].price_unit,
        "SO's price_unit different PO price_unit")
        self.assertTrue(inter_company_sale_order.order_line[0].product_uom_qty == self.purchase_order.order_line[0].product_qty,
        "SO's quantity different PO quantity")
        self.assertTrue(inter_company_sale_order.order_line[0].tax_id[0] == self.vendor_tax_15_sale,
        "Error compute tax for vendor")
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

        self.assertTrue(inter_company_purchase_order.order_line[0].price_unit == self.sale_order.order_line[0].price_unit,
        "SO's price_unit different PO price_unit")
        self.assertTrue(inter_company_purchase_order.order_line[0].product_qty == self.sale_order.order_line[0].product_uom_qty,
        "SO's quantity different PO quantity")
        self.assertTrue(inter_company_purchase_order.order_line[0].taxes_id[0] == self.customer_tax_15_purchase,
        "Error compute tax for customer")

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

    def test_07_sale_manager_create_po_difference_company(self):
        """
            When create a SO to customer is an inter-company, when click button confirm.
            A draft PO will be auto generated in that company.
        """
        context = self.sale_manager._context.copy()
        context['allowed_company_ids'] = [self.vendor_company.id]
        
        new_sale_order = self.env['sale.order'].with_context(context).with_user(self.sale_manager).create({
            'partner_id': self.customer_company.partner_id.id,
            'order_line': [(0,0,{
                'product_id': self.product_test_01.id,
                'product_uom_qty': 2,
                'price_unit': 150.0,
            })]
        })
        new_sale_order.action_confirm()
        self.assertTrue(new_sale_order.inter_comp_purchase_order_id,
                    "Validated purchase order of Customer Company should be created correlative with sale order of Vendor Company")
    
    def test_08_purchase_manager_create_so_difference_company(self):
        """
            When create a PO to vendor is an inter-company, when click button confirm order.
            A draft SO will be auto generated in that company.
        """
        context = self.purchase_manager._context.copy()
        context['allowed_company_ids'] = [self.customer_company.id]

        new_purchase_order = self.env['purchase.order'].with_context(context).with_user(self.purchase_manager).create({
            'partner_id': self.vendor_company.partner_id.id,
            'order_line': [(0,0,{
                'name': 'Purchase Order Line',
                'product_id': self.product_test_02.id,
                'product_qty': 2,
                'price_unit': 200.0,
                'product_uom': self.ref('uom.product_uom_unit'),
                'date_planned': fields.date.today(),
            })]
        })
        new_purchase_order.button_approve()
        self.assertTrue(new_purchase_order.inter_comp_sale_order_id,
                    "Validated sale order of Vender Company should be created correlative with purchase order of Customer Company")
