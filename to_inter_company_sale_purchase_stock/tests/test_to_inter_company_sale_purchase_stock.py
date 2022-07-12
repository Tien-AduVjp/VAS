from odoo.tests import tagged
from odoo.exceptions import UserError

from odoo.addons.to_inter_company_sale_purchase.tests.common import Common


@tagged('post_install','-at_install')
class TestToInterCompanySalePurchaseStock(Common):

    def setUp(self):
        super(TestToInterCompanySalePurchaseStock, self).setUp()
        self.product_test_01.write({'type':'product'})
        self.product_test_02.write({'type':'product'})

        self.purchase_manager.update({
            'groups_id':[(4, self.ref('stock.group_stock_manager'), 0)]
        })
        self.sale_manager.update({
            'groups_id':[(4, self.ref('stock.group_stock_manager'), 0)]
        })
        self.vendor_company_warehouse = self.env['stock.warehouse'].create({
            'name':'Vendor Inter Company Warehouse',
            'code':'OUT',
            'company_id':self.sale_manager.company_id.id
        })
        self.customer_company_warehouse = self.env['stock.warehouse'].create({
            'name':'Customer Inter Company Warehouse',
            'code':'IN',
            'company_id':self.purchase_manager.company_id.id
        })

    def test_01_generate_po_with_inter_company_warehouse(self):
        """
            When create a SO to customer is an inter-company with inter_company_warehouse_id was set,
            a PO will be auto generated in customer company with operation type is was set.
        """
        self.customer_company.update({
            'inter_comp_warehouse_id':self.customer_company_warehouse.id
        })
        self.sale_order.action_confirm()
        inter_company_purchase_order = self.env['purchase.order'].search(
            [
                ('company_id','=',self.customer_company.id),
                ('inter_comp_sale_order_id','=',self.sale_order.id)
            ])
        picking_type = self.env['stock.picking.type'].search([
            ('code', '=', 'incoming'), ('warehouse_id', '=', self.customer_company_warehouse.id)
        ], limit=1)
        self.assertEqual(inter_company_purchase_order.picking_type_id,picking_type,
        "PO should be use operation type of inter-company warehouse.")

    def test_02_generate_po_with_inter_company_warehouse(self):
        """raise UserError if inter-company not setting for inter-warehouse."""
        self.customer_company.update({
            'inter_comp_warehouse_id':False
        })
        with self.assertRaises(UserError):
            self.sale_order.action_confirm()

    def test_03_generate_so_with_inter_company_warehouse(self):
        """
            When create a PO to vendor is an inter-company with inter_comp_warehouse_id was set,
            a SO will be auto generated in vendor company with warehouse is inter_company_warehouse
        """
        self.vendor_company.update({
            'inter_comp_warehouse_id':self.vendor_company_warehouse.id
        })
        self.purchase_order.button_confirm()
        inter_company_sale_order = self.env['sale.order'].search(
            [
                ('company_id','=',self.vendor_company.id),
                ('inter_comp_purchase_order_id','=',self.purchase_order.id)
            ])
        self.assertEqual(inter_company_sale_order.warehouse_id,self.vendor_company_warehouse,
        "SO should be use warehouse was set in inter-company warehouse")

    def test_04_generate_so_with_inter_company_warehouse(self):
        """raise UserError if inter-company not setting for inter-warehouse."""
        self.vendor_company.update({
            'inter_comp_warehouse_id':False
        })
        with self.assertRaises(UserError):
            self.purchase_order.button_confirm()
