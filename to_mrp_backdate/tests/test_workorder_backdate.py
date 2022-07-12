from datetime import datetime, timedelta
from odoo import fields
from odoo.exceptions import UserError

from .common import TestCommon


class WorkorderBackdate(TestCommon):

    @classmethod
    def setUpClass(cls):
        super(WorkorderBackdate, cls).setUpClass()

        cls.mo = cls.generate_mo(cls.product_final, cls.bom_route)
        cls.mo.button_plan()
        cls.workorders = cls.mo.workorder_ids.with_context(open_mrp_workorder_backdate_wizard=True)  # 1 record

    def _prepare_wizard_workorder(self, wo, source_action, backdate):
        wizard = self.env['mrp.workorder.backdate.wizard'].create({
            'mrp_wo_id': wo.id,
            'source_action': source_action,
            'date': backdate
        })
        return wizard

    def test_popup_start_workorder(self):
        #Test popup start WO with admin mrp
        mrp_backdate = self.workorders.with_user(self.user_mrp_manager).button_start()
        self.assertEqual(mrp_backdate.get('res_model'), 'mrp.workorder.backdate.wizard')

        #Test popup start WO with user mrp backdate
        mrp_backdate = self.workorders.with_user(self.user_mrp_backdate).button_start()
        self.assertEqual(mrp_backdate.get('res_model'), 'mrp.workorder.backdate.wizard')

        #Test popup start WO with user mrp
        mrp_backdate = self.workorders.with_user(self.user_mrp_user).button_start()
        self.assertTrue(mrp_backdate)

    def test_popup_pending_workorder(self):
        #Test popup start WO with admin mrp
        mrp_backdate = self.workorders.with_user(self.user_mrp_manager).button_pending()
        self.assertEqual(mrp_backdate.get('res_model'), 'mrp.workorder.backdate.wizard')

        #Test popup start WO with user mrp backdate
        mrp_backdate = self.workorders.with_user(self.user_mrp_backdate).button_pending()
        self.assertEqual(mrp_backdate.get('res_model'), 'mrp.workorder.backdate.wizard')

        #Test popup start WO with user mrp
        mrp_backdate = self.workorders.with_user(self.user_mrp_user).button_pending()
        self.assertTrue(mrp_backdate)

    def test_popup_unblock_workcenter(self):
        #Test popup start WO with admin mrp
        mrp_backdate = self.workorders.with_user(self.user_mrp_manager).button_unblock()
        self.assertEqual(mrp_backdate.get('res_model'), 'mrp.workorder.backdate.wizard')

        #Test popup start WO with user mrp backdate
        mrp_backdate = self.workorders.with_user(self.user_mrp_backdate).button_unblock()
        self.assertEqual(mrp_backdate.get('res_model'), 'mrp.workorder.backdate.wizard')

        #Test popup start WO with user mrp => don't display popup
        with self.assertRaises(UserError):
            self.workorders.with_user(self.user_mrp_user).button_unblock()

    def test_popup_mark_done_workorder(self):
        #Test popup start WO with admin mrp
        mrp_backdate = self.workorders.with_user(self.user_mrp_manager).button_finish()
        self.assertEqual(mrp_backdate.get('res_model'), 'mrp.workorder.backdate.wizard')

        #Test popup start WO with user mrp backdate
        mrp_backdate = self.workorders.with_user(self.user_mrp_backdate).button_finish()
        self.assertEqual(mrp_backdate.get('res_model'), 'mrp.workorder.backdate.wizard')

        #Test popup start WO with user mrp
        mrp_backdate = self.workorders.with_user(self.user_mrp_user).button_finish()
        self.assertTrue(mrp_backdate)

    def test_backdate_01_start_workorder(self):
        """
        Input:
            Bắt đầu hoạt động sx với ngày backdate 3/1/2021 8:00
        Output:
            Ngày bắt đầu của lệnh SX, hoạt động SX là ngày backdate 3/1/2021 8:00
        """
        backdate = fields.Datetime.to_datetime('2021-01-03 08:00:00')
        wo_data = {
            'date_planned_start': backdate,
            'date_planned_finished': self.workorders.date_planned_finished
        }
        mo_data = {
            'date_planned_start': backdate,
            'date_planned_finished': self.mo.date_planned_finished
        }

        # start workorder with backdate
        self._prepare_wizard_workorder(self.workorders, 'button_start', backdate).process()

        # check records
        wo_data.update({
            'date_start': backdate,
            'state': 'progress'
        })
        mo_data.update({
            'date_start': False,
            'state': 'progress'
        })
        self.assertEqual(self.workorders.time_ids[:1].date_start, backdate, "Backdate Productivity generated when start is wrong!")
        self.assertRecordValues(self.mo, [mo_data])
        self.assertRecordValues(self.workorders, [wo_data])

    def test_backdate_02_pending_workorder(self):
        # start workorder with backdate
        self._prepare_wizard_workorder(self.workorders, 'button_start', fields.Datetime.to_datetime('2021-01-03 08:00:00')).process()

        # pending workorder with backdate
        backdate = fields.Datetime.to_datetime('2021-01-03 08:30:00')
        self._prepare_wizard_workorder(self.workorders, 'button_pending', backdate).process()

        self.assertFalse(self.workorders.date_finished)
        reduce_productivity = self.workorders.time_ids.filtered(lambda r: r.loss_id)
        self.assertEqual(set(reduce_productivity.mapped('date_end')), {backdate}, "Backdate when pending WO is wrong!")

    def test_backdate_03_block_workcenter(self):
        # start workorder with backdate
        self._prepare_wizard_workorder(self.workorders, 'button_start', fields.Datetime.to_datetime('2021-01-03 08:00:00')).process()
        backdate = fields.Datetime.to_datetime('2021-01-03 08:30:00')
        productivities_all_wo = self.workcenter.time_ids.filtered(lambda r: r.date_end == False)

        # Block work center
        # Test constraint backdate future
        with self.assertRaises(UserError), self.cr.savepoint():
            self.env['mrp.workcenter.productivity'].create({
                'workcenter_id': self.workorders.workcenter_id.id,
                'loss_id': self.loss_block_type.id,
                'backdate': datetime.now() + timedelta(days=1)
            })

        # Test Block work center
        block_productivity = self.env['mrp.workcenter.productivity'].create({
            'workcenter_id': self.workorders.workcenter_id.id,
            'loss_id': self.loss_block_type.id,
            'backdate': backdate
        })
        block_productivity.button_block()

        self.assertEqual(block_productivity.date_start, backdate, "Backdate when block work center is wrong!")
        self.assertEqual(set(productivities_all_wo.mapped('date_end')), {backdate}, "Backdate when block work center is wrong!")

    def test_backdate_04_unblock_workcenter(self):
        # start workorder with backdate
        self._prepare_wizard_workorder(self.workorders, 'button_start', fields.Datetime.to_datetime('2021-01-03 08:00:00')).process()

        # Block work center
        block_productivity = self.env['mrp.workcenter.productivity'].create({
            'workcenter_id': self.workorders.workcenter_id.id,
            'loss_id': self.loss_block_type.id,
            'backdate': fields.Datetime.to_datetime('2021-01-03 08:30:00')
        })
        block_productivity.button_block()

        # Unblock work center
        backdate = fields.Datetime.to_datetime('2021-01-03 09:00:00')
        self._prepare_wizard_workorder(self.workorders, 'button_unblock', backdate).process()

        self.assertEqual(block_productivity.date_end, backdate, "Backdate when unblock work center is wrong!")

    def test_backdate_05_mark_done_workorder(self):
        # start workorder with backdate
        backdate = fields.Datetime.to_datetime('2021-01-03 08:30:00')
        self._prepare_wizard_workorder(self.workorders, 'button_start', fields.Datetime.to_datetime('2021-01-03 08:00:00')).process()
        wo_date = {
            'date_planned_start': self.workorders.date_planned_start,
            'date_planned_finished': backdate,
            'date_start': self.workorders.date_start
        }
        mo_data = {
            'date_planned_start': self.mo.date_planned_start,
            'date_planned_finished': backdate,
            'date_start': self.mo.date_start,
            'date_finished': self.mo.date_finished,
        }

        # Mark done WO with backdate
        self._prepare_wizard_workorder(self.workorders, 'button_finish', backdate).process()

        # check records
        wo_date.update({
            'date_finished': backdate,
            'state': 'done'
        })
        mo_data['state'] = 'to_close'
        self.assertRecordValues(self.workorders, [wo_date])
        self.assertRecordValues(self.mo, [mo_data])
