import datetime

from odoo import fields
from odoo.tests.common import Form
from odoo.tools.float_utils import float_is_zero

from contextlib import contextmanager
from unittest.mock import patch

from odoo.addons.stock_account.tests.test_stockvaluation import _create_accounting_data
from odoo.addons.stock_account.tests.test_stockvaluationlayer import TestStockValuationCommon


class TestStockAssetCommon(TestStockValuationCommon):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.stock_input_account,\
        cls.stock_output_account,\
        cls.stock_valuation_account,\
        cls.expense_account,\
        cls.stock_journal = _create_accounting_data(cls.env)

        cls.expenses_journal = cls.env['account.journal'].create({
            'name': 'Expenses - Test',
            'code': 'TEXJ',
            'type': 'purchase',
            'default_debit_account_id': cls.expense_account.id,
            'default_credit_account_id': cls.expense_account.id})

        cls.asset_category = cls.env['account.asset.category'].create(
            cls._prepare_asset_category_vals(cls)
            )
        cls.product_comsu = cls.env['product.product'].create({'type': 'consu',
                                                                'name': 'product_consu'})
        cls.product1 = cls.env['product.product'].create({
            'name': 'Product A',
            'type': 'product',
            'tracking': 'serial',
            'default_code': 'prda',
            'categ_id': cls.env.ref('product.product_category_all').id,
            'asset_category_id': cls.asset_category.id,
        })

        cls.product1.categ_id.write({'property_valuation': 'real_time',
                                      'property_cost_method': 'fifo',
                                      })
        cls.product1.write({
            'property_account_expense_id': cls.expense_account.id,
        })
        cls.product1.categ_id.write({
            'property_stock_account_input_categ_id': cls.stock_input_account.id,
            'property_stock_account_output_categ_id': cls.stock_output_account.id,
            'property_stock_valuation_account_id': cls.stock_valuation_account.id,
            'property_stock_journal': cls.stock_journal.id,
        })

        cls.picking_type_asset = cls.env['stock.picking.type'].search(
            [('code', '=', 'asset_allocation')],
            limit=1
            )
        cls.asset_location = cls.env.ref('to_stock_asset.stock_location_asset')

        # Counter automatically incremented by `_generate_sn`
        cls.sn_count = 1

    @contextmanager
    def mocked_today(self, forced_today):
        ''' Helper to make easily a python "with statement" mocking the "today" date.
        :param forced_today:    The expected "today" date as a str or Date object.
        :return:                An object to be used like 'with self.mocked_today(<today>):'.
        '''

        if isinstance(forced_today, str):
            forced_today_date = fields.Date.from_string(forced_today)
            forced_today_datetime = fields.Datetime.from_string(forced_today)
        elif isinstance(forced_today, datetime.datetime):
            forced_today_datetime = forced_today
            forced_today_date = forced_today_datetime.date()
        else:
            forced_today_date = forced_today
            forced_today_datetime = datetime.datetime.combine(forced_today_date, datetime.time())

        def today(*args, **kwargs):
            return forced_today_date

        with patch.object(fields.Date, 'today', today):
            with patch.object(fields.Date, 'context_today', today):
                with patch.object(fields.Datetime, 'now', return_value=forced_today_datetime):
                    yield

    def _make_in_picking_with_serial_product(self, product, quantity, price_unit, serials=[]):
        """ Helper to create in picking with product that is enabled serial.
        """
        move = self.env['stock.move'].create({
            'name': 'in %s' % str(quantity),
            'product_id': product.id,
            'location_id': self.supplier_location.id,
            'location_dest_id': self.stock_location.id,
            'product_uom': self.uom_unit.id,
            'product_uom_qty': quantity,
            'picking_type_id': self.picking_type_in.id,
            'price_unit': price_unit,
        })

        picking = self.env['stock.picking'].create({
            'picking_type_id': move[0].picking_type_id.id,
            'immediate_transfer': True,
            'location_id': move[0].location_id.id,
            'location_dest_id': move[0].location_dest_id.id,
            'move_lines': [(6, 0, move.ids)],
        })

        serials_length = len(serials)
        move_form = Form(move, view='stock.view_stock_move_nosuggest_operations')
        for i in range(int(move.product_uom_qty)):
            with move_form.move_line_nosuggest_ids.new() as line:
                line.lot_name = serials_length > i and serials[i] or 'sn0000%s' % self.sn_count
                self.sn_count += 1
        move = move_form.save()

        picking.button_validate()
        return picking

    def _make_out_picking_as_asset(self, product, quantity):
        """ Helper to create out picking as asset.
        """
        out_move = self.env['stock.move'].create({
            'name': 'out %s units' % str(quantity),
            'product_id': product.id,
            'location_id': self.stock_location.id,
            'location_dest_id': self.asset_location.id,
            'product_uom': self.uom_unit.id,
            'product_uom_qty': quantity,
            'picking_type_id': self.picking_type_asset.id,
        })

        picking = self.env['stock.picking'].create({
            'picking_type_id': out_move.picking_type_id.id,
            'location_id': out_move.location_id.id,
            'location_dest_id': out_move.location_dest_id.id,
        })
        out_move.write({'picking_id': picking.id})
        picking.action_assign()
        return picking

    def _validate_picking(self, picking):
        res = picking.button_validate()
        if res:
            if res['res_model'] == 'stock.immediate.transfer':
                self.env['stock.immediate.transfer'].browse(res['res_id']).process()
            elif res['res_model'] == 'stock.overprocessed.transfer':
                self.env['stock.overprocessed.transfer'].browse(res['res_id']).action_confirm()

    def _force_serial_on_move_line(self, move_line, lot_name):
        """ Helper to force serial on stock move line after picking has been assigned.
        """
        move_line.lot_id = self.env['stock.production.lot'].search([('name', '=', lot_name)], limit=1)

    def _make_return_picking(self, picking, quantity=1.0):
        """ Helper to create return picking on out picking that contains asset.
        """
        stock_return_picking_form = Form(self.env['stock.return.picking']
            .with_context(active_ids=picking.ids, active_id=picking.ids[0],
            active_model='stock.picking'))
        stock_return_picking = stock_return_picking_form.save()
        stock_return_picking = stock_return_picking_form.save()
        stock_return_picking.product_return_moves.quantity = quantity
        stock_return_picking_action = stock_return_picking.create_returns()
        return_pick = self.env['stock.picking'].browse(stock_return_picking_action['res_id'])

        for line in return_pick.move_lines.move_line_ids:
            if float_is_zero(quantity, precision_rounding=0.01):
                break
            line.qty_done = 1.0
            quantity -= 1.0
        return return_pick

    def _prepare_asset_category_vals(self):
        return {
            'name': 'Fixed Assets Category',
            'journal_id': self.stock_journal.id,
            'method_number': 12,
            'method_period': 1,
            'date_first_depreciation': 'last_day_period',
            'asset_account_id': self.stock_input_account.id,
            'depreciation_account_id': self.stock_input_account.id,
            'depreciation_expense_account_id': self.expense_account.id,
            'revaluation_increase_account_id': self.stock_input_account.id,
            'revaluation_decrease_account_id': self.expense_account.id,
            'stock_input_account_id': self.stock_input_account.id,
            'open_asset': True,
            'prorata': True,
            }

    def _search_asset_is_in_draft(self, lots):
        return self.env['account.asset.asset'].search([('production_lot_id', 'in', lots.ids),
                                                       ('state', '=', 'draft')])
