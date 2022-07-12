from datetime import datetime, timedelta

from odoo.tests import tagged
from odoo.exceptions import UserError

from odoo.addons.to_stock_picking_backdate.tests.common import TestCommon

from odoo.addons.stock_account.tests import test_stockvaluation


@tagged('post_install', '-at_install')
class TestBackDate(TestCommon):

    @classmethod
    def setUpClass(cls):
        super(TestBackDate, cls).setUpClass()

        # Update quantity for product B
        cls.env['stock.quant'].create({
            'product_id': cls.productB.id,
            'location_id': cls.stock_location.id,
            'quantity': 100
        })
        
        cls.productC = cls.env['product.product'].create({
            'name': 'Product A',
            'type': 'product',
            'tracking': 'serial',
            'categ_id': cls.categ.id,
            'standard_price': 1000.0
        })
        cls.back_date = datetime(2021, 2, 28)
        
    def test_input_backdate_future(self):
        inventory = self.env['stock.inventory'].create({
            'name': 'productA',
            'location_ids': [(4, self.stock_location.id)],
            'product_ids': [(4, self.productA.id)]
        })
        time_furture = datetime.now() + timedelta(days=1)
        with self.assertRaises(UserError):
            self.env['stock.inventory.backdate.wizard'].create({
                'date': time_furture,
                'accounting_date': time_furture,
                'inventory_id': inventory.id
            })
            
    def test_backdate_inventory_adjustment(self):
        inventory = self.env['stock.inventory'].create({
            'name': 'remove product1',
            'location_ids': [(4, self.stock_location.id)],
            'product_ids': [(4, self.productB.id)]
        })
        inventory.action_start()
        inventory.line_ids[0].product_qty = 101
        
        # Test popup display with user manager
        backdate_wizard = inventory.with_context(open_stock_inventory_backdate_wizard=True).with_user(self.manager_user).action_validate()
        self.assertEqual(backdate_wizard.get('type'), 'ir.actions.act_window', "Popup adjust inventory doesn't display with stock manager!")
        
        # Test time change after confirm backdate wizard
        wz_stock_backdate = self.env['stock.inventory.backdate.wizard'].create({
            'date': self.back_date,
            'accounting_date': self.back_date,
            'inventory_id': inventory.id
        })
        wz_stock_backdate.process()
    
        self.assertEqual(inventory.state, 'done', 'Validate inventory adjustment with backdate wizard not done')
        self.assertEqual(inventory.accounting_date, self.back_date.date(), 'Accounting date not match backdate')
        self.assertEqual(inventory.move_ids[-1:].date, self.back_date, 'Date on stock.move not match backdate')
        self.assertEqual(inventory.move_ids[-1:].move_line_ids[-1:].date, self.back_date, 'Date on stock.move.line not match backdate')
        self.assertEqual(inventory.move_ids[-1:].account_move_ids[-1:].date, self.back_date.date(), 'Date on account move not match backdate')
        self.assertEqual(inventory.move_ids[-1:].stock_valuation_layer_ids.create_date, self.back_date, 'Date on Stock valuation not match backdate')
        
        # Case increase the quantity of a product that is tracked by serial number
        inventory_warn = self.env['stock.inventory'].create({
            'name': 'productC',
            'location_ids': [(4, self.stock_location.id)],
            'product_ids': [(4, self.productC.id)]
        })
        context_adjust = inventory_warn.action_start().get('context', False)
        self.env['stock.inventory.line'].with_context(context_adjust).create({
            'product_uom_id': self.productC.uom_id.id,
            'theoretical_qty': 0,
            'product_qty': 1
        })
        
        wz_stock_backdate_warn = self.env['stock.inventory.backdate.wizard'].create({
            'date': self.back_date,
            'accounting_date': self.back_date,
            'inventory_id': inventory_warn.id
        })
        
        # Get wizard confirm
        wz_initial = self.env['stock.track.confirmation'].search([])
        context_confirm = wz_stock_backdate_warn.process().get('context', False)
        wz_confirm = self.env['stock.track.confirmation'].search([]) - wz_initial
        
        wz_confirm.with_context(context_confirm).action_confirm()

        self.assertEqual(inventory_warn.state, 'done', 'Validate inventory adjustment with backdate wizard not done with product tracking by serial')
        self.assertEqual(inventory_warn.accounting_date, self.back_date.date(), 'Accounting date not match backdate with product tracking by serial')
        self.assertEqual(inventory_warn.move_ids[-1:].date, self.back_date, 'Date on stock.move not match backdate with product tracking by serial')
        self.assertEqual(inventory_warn.move_ids[-1:].move_line_ids[-1:].date, self.back_date, 'Date on stock.move.line not match backdate with product tracking by serial')
        self.assertEqual(inventory_warn.move_ids[-1:].account_move_ids[-1:].date, self.back_date.date(), 'Date on account move not match backdate with product tracking by serial')
        self.assertEqual(inventory_warn.move_ids[-1:].stock_valuation_layer_ids.create_date, self.back_date, 'Date on Stock valuation not match backdate with product tracking by serial')

    def test_popup_backdate_scrap_adjustment(self):
        # Test display popup backdate when validate scrap inventory
        scrap = self.env['stock.scrap'].create({
            'product_id': self.productB.id,
            'scrap_qty': 5,
            'product_uom_id': self.env.ref('uom.product_uom_unit').id,
            'location_id': self.stock_location.id,
            'scrap_location_id': self.customer_location.id
        })
        backdate_wizard = scrap.with_context(open_stock_scrap_backdate_wizard=True).with_user(self.manager_user).action_validate()
        if type(backdate_wizard) == dict:
            self.assertEqual(backdate_wizard.get('type', ''), 'ir.actions.act_window', "Popup scrap doesn't display with stock manager!")
            self.assertEqual(backdate_wizard.get('res_model', ''), 'stock.scrap.backdate.wizard')

        backdate_wizard = scrap.with_context(open_stock_scrap_backdate_wizard=True).with_user(self.stock_user).action_validate()
        if type(backdate_wizard) == dict:
            self.assertEqual(backdate_wizard.get('res_model', ''), 'stock.warn.insufficient.qty.scrap')
        elif type(backdate_wizard) == bool:
            self.assertEqual(backdate_wizard, True, "Popup scrap displayed with stock user!")

    def test_backdate_scrap_adjustment(self):
        # Test time backdate scrap inventory
        scrap = self.env['stock.scrap'].create({
            'product_id': self.productB.id,
            'scrap_qty': 5,
            'product_uom_id': self.env.ref('uom.product_uom_unit').id,
            'location_id': self.stock_location.id,
            'scrap_location_id': self.customer_location.id
        })
        
        wz_scrap_backdate = self.env['stock.scrap.backdate.wizard'].create({
            'date': self.back_date,
            'scrap_id': scrap.id
        })
        wz_scrap_backdate.process()
        
        self.assertEqual(scrap.date_done, self.back_date, 'Time done on scrap not match backdate')
        self.assertEqual(scrap.move_id.date, self.back_date, 'Time stock move after scrap not match backdate')
        self.assertEqual(scrap.move_id.move_line_ids[-1:].date, self.back_date, 'Time stock move line after scrap not match backdate')
        
    def test_backdate_scrap_insufficient_qty(self):
        # Test time backdate scrap in case qty scrap > qty inventory
        scrap = self.env['stock.scrap'].create({
            'product_id': self.productB.id,
            'scrap_qty': 105,
            'product_uom_id': self.env.ref('uom.product_uom_unit').id,
        })
        wz_scrap_backdate = self.env['stock.scrap.backdate.wizard'].create({
            'date': self.back_date,
            'scrap_id': scrap.id
        })
        context_insufficient = wz_scrap_backdate.process().get('context', False)
        wz_scrap_insufficient_qty = self.env['stock.warn.insufficient.qty.scrap'].with_context(context_insufficient).create({})
        wz_scrap_insufficient_qty.action_done()
        
        self.assertEqual(scrap.date_done, self.back_date, 'Time done on scrap not match backdate with qty scrap > qty location')
        self.assertEqual(scrap.move_id.date, self.back_date, 'Time stock move after scrap not match backdate with qty scrap > qty location')
        self.assertEqual(scrap.move_id.move_line_ids[-1:].date, self.back_date, 'Time stock move line after scrap not match backdate with qty scrap > qty location')
