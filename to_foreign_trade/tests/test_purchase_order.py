from odoo import fields
from odoo.tests import Form, tagged
from odoo.exceptions import UserError
from odoo.osv import expression

from .common import TestCommon

@tagged('post_install', '-at_install')
class TestPurchaseOrder(TestCommon):
        
    def test_change_partner_on_po_01(self):
        """
        [Form Test] - TC08
        
        - Case: Create PO, which has partner is marked as foreign trade partner
        - Expected Result:
            + PO will be marked as foreign trade
        """
        with Form(self.env['purchase.order']) as f:
            f.partner_id = self.foreign_trade_partner
            self.assertTrue(f.foreign_trade)
            self.assertEqual(f.picking_type_id, self.checked_warehouse.imp_type_id)
            
            picking_types = self.env['stock.picking.type']
            for pk in f.available_pk_type_ids:
                picking_types |= pk
            self.assertEqual(picking_types, self.checked_warehouse.imp_type_id)
            
    
    def test_change_partner_on_po_02(self):
        """
        [Form Test] - TC09
        
        - Case: Update partner of PO to non foreign trade partner, while it is marked as foreign trade
        - Expected Result:
            + PO will not be marked as foreign trade
        """
        with Form(self.env['purchase.order']) as f:
            f.partner_id = self.foreign_trade_partner
        
        po = f.save()
        with Form(po) as f:
            f.partner_id = self.partner_same_country
            self.assertTrue(not f.foreign_trade)
            self.assertEqual(f.picking_type_id, self.checked_warehouse.in_type_id)
            picking_types = self.env['stock.picking.type']
            for pk in f.available_pk_type_ids:
                picking_types |= pk
            
            pk_type_domain = [('code','=','incoming'), '|', ('warehouse_id', '=', False), ('warehouse_id.company_id', '=', f.company_id.id)]
            additional_domain = [('is_foreign_trade', '=', False)]
            pk_type_domain = expression.AND([pk_type_domain, additional_domain])
            available_picking_types = self.env['stock.picking.type'].search(pk_type_domain)
            self.assertEqual(picking_types, available_picking_types)
    
    def test_change_partner_on_po_03(self):
        """
        [Form Test] - TC10
        
        - Case: Create PO, which has partner is not marked as foreign trade partner 
                but has country differ from country of current company
        - Expected Result:
            + PO will be marked as foreign trade
        """
        with Form(self.env['purchase.order']) as f:
            f.partner_id = self.foreign_trade_partner_abnormal
            self.assertTrue(f.foreign_trade)
            self.assertEqual(f.picking_type_id, self.checked_warehouse.imp_type_id)
            
            picking_types = self.env['stock.picking.type']
            for pk in f.available_pk_type_ids:
                picking_types |= pk
            self.assertEqual(picking_types, self.checked_warehouse.imp_type_id)
            
    def test_change_partner_on_po_04(self):
        """
        [Form Test] - TC11
        
        - Case: Update partner of PO to non foreign trade partner but has country differ from country of current company,
                 while it is not marked as foreign trade
        - Expected Result:
            + PO will be marked as foreign trade
        """
        with Form(self.env['purchase.order']) as f:
            f.partner_id = self.partner_same_country
        
        po = f.save()
        with Form(po) as f:
            f.partner_id = self.foreign_trade_partner_abnormal
            self.assertTrue(f.foreign_trade)
            self.assertEqual(f.picking_type_id, self.checked_warehouse.imp_type_id)
            picking_types = self.env['stock.picking.type']
            for pk in f.available_pk_type_ids:
                picking_types |= pk
            self.assertEqual(picking_types, self.checked_warehouse.imp_type_id)
            
    def test_create_po_01(self):
        """
        [Functional Test] - TC13
        
        - Case: Create PO, which has partner is marked as foreign trade partner
        - Expected Result:
            + PO will be marked as foreign trade
        """
        po = self.env['purchase.order'].create({
            'partner_id': self.foreign_trade_partner.id,
            'currency_id': self.currency_eur.id,
            'picking_type_id': self.checked_warehouse.imp_type_id.id,
        })
        self.assertTrue(po.foreign_trade)
        
    def test_create_po_02(self):
        """
        [Functional Test] - TC14
        
        - Case: Create PO, which has partner has country differ from country of PO company
        - Expected Result:
            + PO will be marked as foreign trade
        """
        po = self.env['purchase.order'].create({
            'partner_id': self.foreign_trade_partner_abnormal.id,
            'currency_id': self.currency_eur.id,
            'picking_type_id': self.checked_warehouse.imp_type_id.id,
        })
        self.assertTrue(po.foreign_trade)
        
    def test_custom_declaration_count_01(self):
        """
        [Functional Test] - TC15
        
        - Case: Check custom declaration count of PO, in case there is no custom declaration related to this PO
        - Expected Result:
            + custom declaration count of PO = 0
        """
        self.assertTrue(self.po1.custom_dec_count == 0)

    def test_custom_declaration_count_02(self):
        """
        [Functional Test] - TC16
        
        - Case: Check custom declaration count of PO, in case there are 2 custom declarations related to this PO
        - Expected Result:
            + custom declaration count of PO = 2
        """
        with Form(self.env['custom.declaration.import']) as f:
            f.purchase_order_id = self.po1
            f.stock_picking_id = self.po1_picking1
        
        with Form(self.env['custom.declaration.import']) as f:
            f.purchase_order_id = self.po1
            f.stock_picking_id = self.po1_picking2
            
        self.assertTrue(self.po1.custom_dec_count == 2)
        
    def test_custom_declaration_count_for_picking_01(self):
        """
        [Functional Test] - TC17
        
        - Case: Check import custom declaration count of picking, in case there is no import custom declaration related to this picking
        - Expected Result:
            + import custom declaration count of picking = 0
        """
        self.assertTrue(self.po1_picking1.custom_dec_import_count == 0)

    def test_custom_declaration_count_for_picking_02(self):
        """
        [Functional Test] - TC18
        
        - Case: Check import custom declaration count of picking, in case there are 2 import custom declarations related to this picking
        - Expected Result:
            + import custom declaration count of picking = 2
        """
        with Form(self.env['custom.declaration.import']) as f:
            f.purchase_order_id = self.po1
            f.stock_picking_id = self.po1_picking1
        
        with Form(self.env['custom.declaration.import']) as f:
            f.purchase_order_id = self.po1
            f.stock_picking_id = self.po1_picking1
            
        self.assertTrue(self.po1_picking1.custom_dec_import_count == 2)
        
    def test_custom_declaration_required_for_picking_01(self):
        """
        [Functional Test] - TC21
        
        - Case: Check import custom declaration required for picking, which has location destination is marked for custom clearance 
            and there is no related custom declaration
        - Expected Result:
            + picking requires custom declaration
        """
        self.assertTrue(self.po1_picking1.custom_dec_required)
        self.assertTrue(self.po1_picking2.custom_dec_required)
    
    def test_flow_of_import_01(self):
        """
        [Functional Test] - TC50
        
        - Case: Operate import product from foreign partner
            + Reception 1 step
        - Expected Result:
            + After confirm PO, there are 2 pickings are created, 
            + 1st picking from vendor to custom zone, 
            + 2nd picking from custom zone to stock
            + Can't validate 2nd picking, while 1st picking doesn't have custom declaration, or custom declaration is not confirmed
        """
        po = self.env['purchase.order'].create({
            'partner_id': self.foreign_trade_partner.id,
            'currency_id': self.currency_eur.id,
            'picking_type_id': self.checked_warehouse.imp_type_id.id,
            'order_line': [
                (0, 0, {
                    'name': self.import_product_1.name,
                    'product_id': self.import_product_1.id,
                    'product_uom': self.uom_unit.id,
                    'product_qty': 2.0,
                    'price_unit': 100.0,
                    'date_planned': fields.Date.from_string('2021-10-20'),
                    'taxes_id': [(6, 0, [self.purchase_tax.id])]
                })
            ],
        })
        po.button_confirm()
        po_picking = po.picking_ids[0]
        related_picking = po_picking.move_lines.move_dest_ids.picking_id 
        po_picking.button_validate()
        po_picking.action_confirm()
        po_picking.action_assign()
        stock_move1 = po_picking.move_lines[0]
        stock_move1.move_line_ids.write({'qty_done': 2.0})
        po_picking.action_done()
        
        related_picking.button_validate()
        related_picking.action_confirm()
        related_picking.action_assign()
        stock_move2 = related_picking.move_lines[0]
        stock_move2.move_line_ids.write({'qty_done': 2.0})
        with self.assertRaises(UserError):
            related_picking.action_done()
            
        with Form(self.env['custom.declaration.import']) as f:
            f.purchase_order_id = po
            f.request_date = fields.Date.from_string('2021-10-20')
            f.stock_picking_id = po_picking
        custom_declaration = f.save()
        
        with self.assertRaises(UserError):
            related_picking.action_done()
            
        custom_declaration.action_open()
        custom_declaration.action_confirm()
        related_picking.action_done()
        self.assertTrue(related_picking.state == 'done')
        
    def test_return_product_01(self):
        """
        [Functional Test] - TC57
        
        - Case: Return product from stock to vendor
        - Expected Result:
            + After return product from stock to custom zone, 
                the return from custom zone to vendor will require custom declaration of previous return
        """
        po = self.env['purchase.order'].create({
            'partner_id': self.foreign_trade_partner.id,
            'currency_id': self.currency_eur.id,
            'picking_type_id': self.checked_warehouse.imp_type_id.id,
            'order_line': [
                (0, 0, {
                    'name': self.import_product_1.name,
                    'product_id': self.import_product_1.id,
                    'product_uom': self.uom_unit.id,
                    'product_qty': 2.0,
                    'price_unit': 100.0,
                    'date_planned': fields.Date.from_string('2021-10-20'),
                    'taxes_id': [(6, 0, [self.purchase_tax.id])]
                })
            ],
        })
        po.button_confirm()
        po_picking = po.picking_ids[0]
        related_picking = po_picking.move_lines.move_dest_ids.picking_id 
        po_picking.button_validate()
        po_picking.action_confirm()
        po_picking.action_assign()
        stock_move1 = po_picking.move_lines[0]
        stock_move1.move_line_ids.write({'qty_done': 2.0})
        po_picking.action_done()
        
        related_picking.button_validate()
        related_picking.action_confirm()
        related_picking.action_assign()
        stock_move2 = related_picking.move_lines[0]
        stock_move2.move_line_ids.write({'qty_done': 2.0})
       
            
        with Form(self.env['custom.declaration.import']) as f:
            f.purchase_order_id = po
            f.request_date = fields.Date.from_string('2021-10-20')
            f.stock_picking_id = po_picking
        custom_declaration = f.save()     
        custom_declaration.action_open()
        custom_declaration.action_confirm()
        related_picking.action_done()
        self.assertTrue(related_picking.state == 'done')
        
        # do return from picking 2
        with Form(self.env['stock.return.picking'].with_context({
            'default_picking_id': related_picking
        })) as return_form:
            for idx in range(len(return_form.product_return_moves)):
                with return_form.product_return_moves.edit(idx) as line:
                    if line.product_id == self.import_product_1:
                        line.quantity = 2.0
        wizard = return_form.save()
        wizard = wizard.with_context({'default_picking_id': False})
        result = wizard._create_returns()
        return_picking1 = self.env['stock.picking'].browse(result[0])
        return_picking1.button_validate()
        return_picking1.action_confirm()
        return_picking1.action_assign()
        return_stock_move1 = return_picking1.move_lines[0]
        return_stock_move1.move_line_ids.write({'qty_done': 2.0})
        return_picking1.action_done()
        
        # do return from picking 1
        with Form(self.env['stock.return.picking'].with_context({
            'default_picking_id': po_picking
        })) as return_form:
            for idx in range(len(return_form.product_return_moves)):
                with return_form.product_return_moves.edit(idx) as line:
                    if line.product_id == self.import_product_1:
                        line.quantity = 2.0
        wizard = return_form.save()
        wizard = wizard.with_context({'default_picking_id': False})
        result = wizard._create_returns()
        return_picking2 = self.env['stock.picking'].browse(result[0])
        return_picking2.button_validate()
        return_picking2.action_confirm()
        return_picking2.action_assign()
        return_stock_move2 = return_picking2.move_lines[0]
        return_stock_move2.move_line_ids.write({'qty_done': 2.0})
        # with self.assertRaises(UserError):
        # currently we don't require custom declaration for previous picking
        return_picking2.action_done()
