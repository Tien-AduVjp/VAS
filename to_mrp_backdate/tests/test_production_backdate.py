from unittest.mock import patch
from odoo import fields
from odoo.tests.common import Form
from .common import TestCommon


class ProductionBackdate(TestCommon):

    def test_display_popup_backdate(self):
        mo = self.generate_mo(self.product_final, self.bom_noroute)
        mo = mo.with_context(open_mrp_markdone_backdate_wizard=True)

        # Popup mark done
        mrp_backdate = mo.with_user(self.user_mrp_backdate).button_mark_done()
        self.assertEqual(mrp_backdate.get('res_model'), 'mrp.markdone.backdate.wizard')
        mrp_backdate = mo.with_user(self.user_mrp_manager).button_mark_done()
        self.assertEqual(mrp_backdate.get('res_model'), 'mrp.markdone.backdate.wizard')
        mrp_backdate = mo.with_user(self.user_mrp_user).button_mark_done()
        self.assertNotEqual(mrp_backdate.get('res_model'), 'mrp.markdone.backdate.wizard')

    def test_backdate_mark_done_01(self):
        """
        Input:
            Lệnh SX với BoM không có hoạt động SX nào
            Xác nhận lệnh sản xuất vơi ngày kế hoạch là 1/1/2021
            Ngày hiện tại
            Hoàn thành lệnh sản xuất với ngày 3/1/2021.
        Output:
            Ngày hoàn thành MO là ngày 3/1/2021
        """
        mo = self.generate_mo(self.product_final, self.bom_noroute)
        backdate = fields.Datetime.to_datetime('2021-01-03 08:00:00')

        wizard_mark_done = self.env['mrp.markdone.backdate.wizard'].create({
            'mrp_order_id': mo.id,
            'date': backdate
        })
        result = wizard_mark_done.process()
        wizard_immediate_production = Form(self.env[result['res_model']].with_context(result['context'])).save()
        wizard_immediate_production.process()
        #test time in stock move, stock move line, stock valuation layer
        date_stock_move_set = set((mo.move_raw_ids + mo.move_finished_ids).mapped('date'))
        self.assertEqual(date_stock_move_set, {backdate}, "Backdate stock move is wrong when mark done MO!")

        date_stock_move_line_set = set((mo.move_raw_ids.move_line_ids + mo.move_finished_ids.move_line_ids).mapped('date'))
        self.assertEqual(date_stock_move_line_set, {backdate}, "Backdate stock move is wrong when mark done MO!")

        stock_value_layers = (mo.move_raw_ids + mo.move_finished_ids).stock_valuation_layer_ids
        self.assertEqual(set(stock_value_layers.mapped('create_date')), {backdate}, "Backdate stock valuation layer is wrong when mark done MO!")

        #test finish date and scheduled date
        self.assertRecordValues(mo,
            [{
                'date_finished': backdate,
                'date_planned_start': fields.Datetime.to_datetime('2021-01-01')
            }])

    def test_backdate_mark_done_02(self):
        """
        Input:
            Xác nhận lệnh sản xuất vơi ngày kế hoạch là 1/1/2021
            Không Lập kế hoạch SX
            Ngày hiện tại 5/1/2021
            Hoàn thành lệnh sản xuất với ngày 3/1/2021.
        Output:
            Ngày kế hoạch bắt đầu và ngày hoàn thành MO là ngày 3/1/2021
            Ngày bắt đầu - kết thúc, ngày kế hoạch bắt đầu - kết thúc của hoạt động sản xuất là ngày 3/1/2021
        """
        mo = self.generate_mo(self.product_final, self.bom_route)
        backdate = fields.Datetime.to_datetime('2021-01-03 08:00:00')

        wizard_mark_done = self.env['mrp.markdone.backdate.wizard'].create({
            'mrp_order_id': mo.id,
            'date': backdate
        })
        result = wizard_mark_done.process()
        wizard_immediate_production = Form(self.env[result['res_model']].with_context(result['context'])).save()
        wizard_immediate_production.process()
        #test time in stock move, stock move line, stock valuation layer
        date_stock_move_set = set((mo.move_raw_ids + mo.move_finished_ids).mapped('date'))
        self.assertEqual(date_stock_move_set, {backdate}, "Backdate stock move is wrong when mark done MO!")

        date_stock_move_line_set = set((mo.move_raw_ids.move_line_ids + mo.move_finished_ids.move_line_ids).mapped('date'))
        self.assertEqual(date_stock_move_line_set, {backdate}, "Backdate stock move is wrong when mark done MO!")

        stock_value_layers = (mo.move_raw_ids + mo.move_finished_ids).stock_valuation_layer_ids
        self.assertEqual(set(stock_value_layers.mapped('create_date')), {backdate}, "Backdate stock valuation layer is wrong when mark done MO!")

        # Test MO
        self.assertRecordValues(mo,
            [{
                'date_finished': backdate,
                'date_planned_start': backdate
            }])
        # Test Workorders
        self.assertRecordValues(mo.workorder_ids,
            [{
                'date_start': backdate,
                'date_finished': backdate,
                'date_planned_start': backdate,
                'date_planned_finished': backdate
            }])

    def test_backdate_mark_done_03(self):
        """
        Input:
            Xác nhận lệnh sản xuất vơi ngày kế hoạch là 1/1/2021
            Lập kế hoạch SX
            Không bắt đầu hoạt động sản xuất nào
            Ngày hiện tại 5/1/2021
            Hoàn thành lệnh sản xuất với ngày 3/1/2021.
        Output:
            Ngày hoàn thành MO là ngày 3/1/2021
            Ngày hoàn thành và kết thúc của hoạt động sản xuất là ngày 3/1/2021

        * Không test ngày kế hoạch bắt đầu - kết thúc ở đây vì:
            - Không thể mock vào thư viện datetime của python khi thay đổi env, nên giá trị là ngày giờ hiện tại tại thời điểm chạy test
            - module này không áp dụng backdate cho tính năng lập kế hoạch trên MO
        """
        mo = self.generate_mo(self.product_final, self.bom_route)
        mo.button_plan()

        with patch.object(fields.Datetime, 'now', lambda: fields.Datetime.to_datetime('2021-01-05 08:00:00')):
            backdate = fields.Datetime.to_datetime('2021-01-03 08:00:00')

            wizard_mark_done = self.env['mrp.markdone.backdate.wizard'].create({
                'mrp_order_id': mo.id,
                'date': backdate
            })
            result = wizard_mark_done.process()
            wizard_immediate_production = Form(self.env[result['res_model']].with_context(result['context'])).save()
            wizard_immediate_production.process()
            #test time in stock move, stock move line, stock valuation layer
            date_stock_move_set = set((mo.move_raw_ids + mo.move_finished_ids).mapped('date'))
            self.assertEqual(date_stock_move_set, {backdate}, "Backdate stock move is wrong when mark done MO!")

            date_stock_move_line_set = set((mo.move_raw_ids.move_line_ids + mo.move_finished_ids.move_line_ids).mapped('date'))
            self.assertEqual(date_stock_move_line_set, {backdate}, "Backdate stock move is wrong when mark done MO!")

            stock_value_layers = (mo.move_raw_ids + mo.move_finished_ids).stock_valuation_layer_ids
            self.assertEqual(set(stock_value_layers.mapped('create_date')), {backdate}, "Backdate stock valuation layer is wrong when mark done MO!")

            # Test MO
            self.assertEqual(mo.date_finished, backdate)
            # Test Workorders
            self.assertRecordValues(mo.workorder_ids,
                [{
                    'date_start': backdate,
                    'date_finished': backdate,
                }])
