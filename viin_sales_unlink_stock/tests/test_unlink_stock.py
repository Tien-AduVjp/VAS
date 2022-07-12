from odoo.tests import Form, TransactionCase, tagged
from odoo.exceptions import UserError

@tagged('post_install', '-at_install')
class TestSalesUnlinkStock(TransactionCase):

    def setUp(self):
        super(TestSalesUnlinkStock, self).setUp()
        
        # Enable feature prevent unlink
        self.env.company.prevent_unlink_related_pickings = True

        # Create data for SO
        Product = self.env['product.product'].with_context(default_type='product')
        product = Product.create({'name': 'pd1'})
        product2 = Product.create({'name': 'pd2'})         
        inventory_wizard = self.env['stock.change.product.qty'].create({
            'product_id': product.id,
            'product_tmpl_id': product.product_tmpl_id.id,
            'new_quantity': 100,
        })
        inventory_wizard.change_product_qty()
        
        inventory_wizard = self.env['stock.change.product.qty'].create({
            'product_id': product2.id,
            'product_tmpl_id': product2.product_tmpl_id.id,
            'new_quantity': 100,
        })
        inventory_wizard.change_product_qty()
        
        partner = self.env.ref('base.res_partner_1')

        # Create data SO
        so = Form(self.env['sale.order'])
        so.partner_id = partner
        with so.order_line.new() as so_line:
            so_line.product_id = product
            so_line.price_unit = 1000
            so_line.product_uom_qty = 3
            
        with so.order_line.new() as so_line:
            so_line.product_id = product2
            so_line.price_unit = 1000
            so_line.product_uom_qty = 3
            
        self.so = so.save()
        self.so.action_confirm()
        
        # To avoid any other constraints, set state sale order to draft.
        self.so.state = 'draft'

    def validate_picking(self, pickings):
        for move in pickings.move_ids_without_package:
            move.quantity_done = move.product_uom_qty
        wz_validate = self.env['stock.immediate.transfer'].create({
            'pick_ids': [(6, 0, pickings.ids)]
        })
        wz_validate.process()

    def test_unlink_case_remove_picking(self):
        # Can't unlink SO linking a Picking
        with self.assertRaises(UserError):
            self.so.unlink()

        # Unlink stock picking to remove SO linking
        self.so.picking_ids.unlink()
        
        # Can remove SO
        self.so.unlink()
        
    def test_unlink_case_remove_stock_move(self):
        # Set cancel picking state to remove stock_move
        self.so.picking_ids.action_cancel()
        
        # Can't remove SO although Picking linking in cancel state
        with self.assertRaises(UserError):
            self.so.unlink()
        
        # Unlink all stock_move to remove SO linking
        self.so.picking_ids.move_ids_without_package.unlink()
        
        # Can remove SO
        self.so.unlink()
    
    def test_unlink_so_line_if_decrease_qty(self):
        self.so.order_line[-1:].product_uom_qty = 1
        self.so.order_line.unlink()
    
    def test_unlink_so_line_if_validate_and_decrease_qty(self):
        self.validate_picking(self.so.picking_ids)
        self.so.order_line[-1:].product_uom_qty = 1
        self.so.order_line.unlink()
    
    def test_unlink_so_line_if_decrease_zero_qty(self):
        self.so.order_line[-1:].product_uom_qty = 0
        self.so.order_line.unlink()
    
    def test_unlink_so_line_if_validate_and_decrease_zero_qty(self):
        self.validate_picking(self.so.picking_ids)
        self.so.order_line[-1:].product_uom_qty = 0
        self.so.order_line.unlink()
    
    def test_unlink_so_line_if_increase_qty(self):
        self.so.order_line[-1:].product_uom_qty = 10
        self.so.order_line.unlink()
    
    def test_unlink_so_line_if_validate_and_increase_qty(self):
        self.validate_picking(self.so.picking_ids)
        self.so.order_line[-1:].product_uom_qty = 10
        self.so.order_line.unlink()
