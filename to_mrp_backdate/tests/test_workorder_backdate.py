from datetime import datetime, timedelta

from odoo.exceptions import UserError

from .common import TestCommon


class WorkorderBackdate(TestCommon):
    
    def _prepare_wizard_workorder(self, wo, source_action, backdate):
        wizard = self.env['mrp.workorder.backdate.wizard'].create({
            'mrp_wo_id': wo.id,
            'source_action': source_action,
            'date': backdate
        })
        return wizard
            
    def test_popup_01_start_workorder(self):
        #Set date_planned_start WO to fit time test
        self.workorder1.date_planned_start = datetime.now()
                
        #Test popup start WO with admin mrp
        mrp_backdate = self.workorder1.with_user(self.user_mrp_manager).button_start()
        self.assertEqual(mrp_backdate.get('type'), 'ir.actions.act_window', "Popup start workorder not display with mrp manager!")
        
        #Test popup start WO with user mrp
        mrp_backdate = self.workorder1.with_user(self.user_mrp_user).button_start()
        self.assertEqual(mrp_backdate, True, "Popup start workorder displayed with mrp user!")
        
    def test_popup_02_pending_workorder(self):        
        #Test popup pending WO with admin mrp
        mrp_backdate = self.workorder1.with_user(self.user_mrp_manager).button_pending()
        self.assertEqual(mrp_backdate.get('type'), 'ir.actions.act_window', "Popup pending workorder not display with mrp manager!")
        
        #Test popup pending WO with user mrp
        mrp_backdate = self.workorder1.with_user(self.user_mrp_user).button_pending()
        self.assertEqual(mrp_backdate, True, "Popup pending workorder displayed with mrp user!")

    def test_popup_03_unblock_workcenter(self):
        #Test Popup resume WO after pending in previous step
        self.test_popup_01_start_workorder()
        
        #Block workcenter
        block_productivity = self.env['mrp.workcenter.productivity'].create({
            'workcenter_id': self.workorder1.workcenter_id.id,
            'loss_id': self.env.ref('mrp.block_reason1').id
        })
        block_productivity.button_block()
        
        #Test popup block WO with admin mrp
        mrp_backdate = self.workorder1.with_user(self.user_mrp_manager).button_unblock()
        self.assertEqual(mrp_backdate.get('type'), 'ir.actions.act_window', "Popup unblock workorder not display with mrp manager!")
        
        #Test popup block WO with user mrp
        mrp_backdate = self.workorder1.with_user(self.user_mrp_user).button_unblock()
        self.assertEqual(mrp_backdate, True, "Popup unblock workorder displayed with mrp user!")

    def test_popup_04_mark_done_workorder(self):
        #Test Popup resume WO after unblock in previous step
        self.test_popup_01_start_workorder()
        
        #Done workorder
        self.workorder1.record_production()
        
        #Test popup mark done WO with admin mrp
        mrp_backdate = self.workorder1.with_user(self.user_mrp_manager).button_finish()
        self.assertEqual(mrp_backdate.get('type'), 'ir.actions.act_window', "Popup unblock workorder not display with mrp manager!")
        
        #Test popup mark done WO with user mrp
        mrp_backdate = self.workorder1.with_user(self.user_mrp_user).button_finish()
        self.assertEqual(mrp_backdate, True, "Popup unblock workorder displayed with mrp user!")
        
    def test_backdate_01_start_workorder(self):
        backdate = datetime(2021, 8, 15)
        #start workorder with backdate
        self._prepare_wizard_workorder(self.workorder2, 'button_start', backdate).process()
        productivities_wo = self.workorder2.time_ids.filtered(lambda r: r.date_end == False)
        
        #Set date_planned_start to fit backdate
        self.workorder2.date_planned_start = datetime(2021, 8, 15)

        self.assertEqual(set(productivities_wo.mapped('date_start')), {backdate}, "Backdate Productivity generated when start is wrong!")
        self.assertEqual(self.workorder2.date_start, backdate, "Backdate start of WO is wrong!")
        self.assertEqual(self.mo2.date_start, backdate, "Backdate start of MO after start WO is wrong!")
    
    def test_backdate_02_pending_workorder(self):
        backdate = datetime(2021, 8, 16)
        #pending workorder with backdate
        self._prepare_wizard_workorder(self.workorder2, 'button_pending', backdate).process()

        reduce_productivity = self.workorder2.time_ids.filtered(lambda r: r.loss_id == self.loss_reduce_type)[-1:]
        self.assertEqual(reduce_productivity.date_end, backdate, "Backdate when pending WO is wrong!")
        
    def test_backdate_03_block_workcenter(self):
        backdate = datetime(2021, 8, 17)
        #Resume WO pausing previous step
        self.test_backdate_01_start_workorder()
        
        #Create additional WO and start to generate time productivity at the same workcenter
        mo, workorder = self.generate_mo_with_workorder()
        workorder.with_user(self.user_mrp_user).button_start()

        productivities_all_wo = self.workcenter.time_ids.filtered(lambda r: r.date_end == False)
        
        #Block work center
        #Test constraint backdate future
        with self.assertRaises(UserError), self.cr.savepoint():
            self.env['mrp.workcenter.productivity'].create({
                'workcenter_id': self.workorder2.workcenter_id.id,
                'loss_id': self.loss_block_type.id,
                'backdate': datetime.now() + timedelta(days=1)
            })
        
        block_productivity = self.env['mrp.workcenter.productivity'].create({
            'workcenter_id': self.workorder2.workcenter_id.id,
            'loss_id': self.loss_block_type.id,
            'backdate': backdate
        })
        block_productivity.button_block()
        
        self.assertEqual(block_productivity.date_start, backdate, "Backdate when block work center is wrong!")
        self.assertEqual(set(productivities_all_wo.mapped('date_end')), {backdate}, "Backdate when block work center is wrong!")

    def test_backdate_04_unblock_workcenter(self):
        backdate = datetime(2021, 8, 18)        
        block_productivities = self.workcenter.time_ids.filtered(lambda r: r.loss_id == self.loss_block_type and r.date_end == False)
       
        #Unblock work center
        self._prepare_wizard_workorder(self.workorder2, 'button_unblock', backdate).process()
        
        self.assertEqual(block_productivities.date_end, backdate, "Backdate when unblock work center is wrong!")

    def test_backdate_05_mark_done_workorder(self):
        backdate = datetime(2021, 8, 19)
        #Resume WO pausing by action_block in previous step
        self.test_backdate_01_start_workorder()
        
        #Mark done WO with backdate
        self.workorder2.with_context(open_mrp_workorder_backdate_wizard=True).record_production()
        self._prepare_wizard_workorder(self.workorder2, 'button_finish', backdate).process()
        self.workorder2.invalidate_cache(['date_finished'], self.workorder2.ids)
        
        self.assertEqual(self.workorder2.date_finished, backdate, "Backdate date_finished when mark done WO is wrong!")
        self.assertEqual(self.workorder2.date_planned_finished, backdate, "Backdate date_planned_finish when mark done WO is wrong!")
