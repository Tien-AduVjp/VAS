from datetime import datetime

from .common import TestCommon


class ProductionBackdate(TestCommon):

    def test_display_popup_backdate(self):
        mo = self.generate_mo_opened_produce()
        mo = mo.with_context(open_mrp_inventory_backdate_wizard=True)
        #Popup post inventory
        mrp_backdate = mo.with_user(self.user_mrp_manager).post_inventory()
        self.assertEqual(mrp_backdate.get('type'), 'ir.actions.act_window', "Popup doesn't display with mrp manager!")
        
        mrp_backdate = mo.with_user(self.user_mrp_user).post_inventory()
        self.assertEqual(mrp_backdate, True, "Popup displayed with mrp user!")

        mo = mo.with_context(open_mrp_markdone_backdate_wizard=True)
        #Popup mark done
        mrp_backdate = mo.with_user(self.user_mrp_manager).button_mark_done()
        self.assertEqual(mrp_backdate.get('type'), 'ir.actions.act_window', "Popup doesn't display with mrp manager!")
        
        mrp_backdate = mo.with_user(self.user_mrp_user).button_mark_done()
        self.assertEqual(mrp_backdate, True, "Popup displayed with mrp user!")
    
    def test_time_backdate_post_inventory(self):
        mo = self.generate_mo_opened_produce()
        backdate = datetime(2021, 8, 16)
        #post inventory
        wizard_post_inventory = self.env['mrp.inventory.backdate.wizard'].create({
            'mrp_order_id': mo.id,
            'date': backdate
        })
        wizard_post_inventory.process()
        
        #test time in stock move, stock move line, stock valuation layer
        date_stock_move_set = set((mo.move_raw_ids + mo.move_finished_ids).mapped('date'))
        self.assertEqual(date_stock_move_set, {backdate}, "Backdate stock move is wrong when post inventory MO!")
        
        date_stock_move_line_set = set((mo.move_raw_ids.move_line_ids + mo.move_finished_ids.move_line_ids).mapped('date'))
        self.assertEqual(date_stock_move_line_set, {backdate}, "Backdate stock move is wrong when post inventory MO!")
        
        stock_value_layers = (mo.move_raw_ids + mo.move_finished_ids).stock_valuation_layer_ids
        self.assertEqual(set(stock_value_layers.mapped('create_date')), {backdate}, "Backdate stock valuation layer is wrong when post inventory MO!")

    def test_time_backdate_mark_done(self):
        mo = self.generate_mo_opened_produce()
        backdate = datetime(2021, 7, 31)
        
        wizard_mark_done = self.env['mrp.markdone.backdate.wizard'].create({
            'mrp_order_id': mo.id,
            'date': backdate
        })
        wizard_mark_done.process()
        
        #test time in stock move, stock move line, stock valuation layer
        date_stock_move_set = set((mo.move_raw_ids + mo.move_finished_ids).mapped('date'))
        self.assertEqual(date_stock_move_set, {backdate}, "Backdate stock move is wrong when mark done MO!")
        
        date_stock_move_line_set = set((mo.move_raw_ids.move_line_ids + mo.move_finished_ids.move_line_ids).mapped('date'))
        self.assertEqual(date_stock_move_line_set, {backdate}, "Backdate stock move is wrong when mark done MO!")
        
        stock_value_layers = (mo.move_raw_ids + mo.move_finished_ids).stock_valuation_layer_ids
        self.assertEqual(set(stock_value_layers.mapped('create_date')), {backdate}, "Backdate stock valuation layer is wrong when mark done MO!")
            
        #test time finish
        self.assertEqual(mo.date_finished, backdate, "Backdate finish is wrong when mark done MO!")
