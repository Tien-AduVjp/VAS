from odoo.exceptions import UserError
from odoo.tests import Form
from odoo.tests.common import SavepointCase

from odoo.addons.stock_account.tests.test_stockvaluation import _create_accounting_data


class TestSVLCommon(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestSVLCommon, cls).setUpClass()

        cls.no_mailthread_features_ctx = {
            'no_reset_password': True,
            'tracking_disable': True,
        }
        cls.env = cls.env(context=dict(cls.no_mailthread_features_ctx, **cls.env.context))

        cls.stock_location = cls.env.ref('stock.stock_location_stock')
        cls.customer_location = cls.env.ref('stock.stock_location_customers')
        cls.supplier_location = cls.env.ref('stock.stock_location_suppliers')
        cls.uom_unit = cls.env.ref('uom.product_uom_unit')

        cls.picking_type_in = cls.env.ref('stock.picking_type_in')
        cls.picking_type_out = cls.env.ref('stock.picking_type_out')

        # enable tracking on all product that belong this category
        # to avoid error when using specific identification method
        category_all = cls.env.ref('product.product_category_all')
        products = cls.env['product.product'].search([
            ('categ_id', '=', category_all.id),
            ('tracking', '=', 'none')
            ])
        products.write({'tracking': 'serial'})

        category_all.property_cost_method = 'specific_identification'

        Product = cls.env['product.product']
        cls.product_serial = Product.create({
            'name': 'Tracked by SN',
            'type': 'product',
            'tracking': 'serial',
            'categ_id': cls.env.ref('product.product_category_all').id
        })
        cls.product_lot = Product.create({
            'name': 'Tracked by Lot',
            'type': 'product',
            'tracking': 'lot',
            'categ_id': cls.env.ref('product.product_category_all').id
        })

        cls.stock_input_account, cls.stock_output_account, cls.stock_valuation_account, cls.expense_account, cls.stock_journal = _create_accounting_data(cls.env)

        (cls.product_serial | cls.product_lot).categ_id.write({
            'property_valuation': 'real_time',
            'property_stock_account_input_categ_id': cls.stock_input_account.id,
            'property_stock_account_output_categ_id': cls.stock_output_account.id,
            'property_stock_valuation_account_id': cls.stock_valuation_account.id,
            'property_stock_journal': cls.stock_journal.id,
            })
        (cls.product_serial | cls.product_lot).write({
            'property_account_expense_id': cls.expense_account.id,
        })

    def setUp(self):
        super(TestSVLCommon, self).setUp()
        # Counter automatically incremented by `_generate_sn` and `_generate_lot`.
        self.lot_count = 1
        self.sn_count = 1

    def _create_in_move(self, product, unit_cost, qty=1):
        return self.env['stock.move'].create({
            'name': 'Move Test',
            'product_id': product.id,
            'product_uom': self.uom_unit.id,
            'product_uom_qty': qty,
            'location_id': self.supplier_location.id,
            'location_dest_id': self.stock_location.id,
            'picking_type_id': self.picking_type_in.id,
            'price_unit': unit_cost,
        })

    def _create_out_move(self, product, qty=1):
        return self.env['stock.move'].create({
            'name': 'Move Test',
            'product_id': product.id,
            'product_uom': self.uom_unit.id,
            'product_uom_qty': qty,
            'location_id': self.stock_location.id,
            'location_dest_id': self.customer_location.id,
            'picking_type_id': self.picking_type_out.id,
        })

    def _generate_sn(self, moves):
        """ Creates a move with move lines, then asks for generates Serial Numbers.
        """
        for move in moves.filtered(lambda m: m.product_id.tracking == 'serial'):
            move_form = Form(move, view='stock.view_stock_move_nosuggest_operations')
            for line in range(int(move.product_uom_qty)):
                with move_form.move_line_nosuggest_ids.new() as line:
                    line.lot_name = 'sn0000%s' % self.sn_count
                    line.qty_done = 1
                    self.sn_count += 1
            move = move_form.save()
        return moves

    def _generate_lot(self, moves, nbre_of_lines):
        """ Creates a move with move lines, then asks for generates Lots.
        """
        for move in moves.filtered(lambda m: m.product_id.tracking == 'lot'):
            move_form = Form(move, view='stock.view_stock_move_nosuggest_operations')
            qty = move.product_uom_qty
            for line in range(int(nbre_of_lines)):
                with move_form.move_line_nosuggest_ids.new() as line:
                    line.lot_name = 'lot0000%s' % self.lot_count
                    line.qty_done = qty / nbre_of_lines
                    self.lot_count += 1
            move = move_form.save()
        return moves

    def _create_picking(self, moves):
        """ Helper to create and validate a receipt move.
        """

        picking = self.env['stock.picking'].create({
            'picking_type_id': moves[0].picking_type_id.id,
            'immediate_transfer': True,
            'location_id': moves[0].location_id.id,
            'location_dest_id': moves[0].location_dest_id.id,
        })
        moves.write({'picking_id': picking.id})
        return picking

    def _make_in_move(self, product, qty, unit_cost, nbre_of_lines, force_lot_id=False):
        in_move = self._create_in_move(product, unit_cost, qty)
        picking = self._create_picking(in_move)
        self._generate_lot(picking.move_lines, nbre_of_lines)
        if force_lot_id:
            in_move.move_line_ids.write({'lot_name': False, 'lot_id': force_lot_id})
        picking.button_validate()
        return in_move

    def _make_out_move(self, product, qty):
        out_move = self._create_out_move(product, qty)
        picking = self._create_picking(out_move)
        picking.action_assign()
        diff = qty - sum(picking.move_line_ids.mapped('product_uom_qty'))
        if diff > 0:
            for line in out_move.move_line_ids[:-1]:
                line.qty_done = line.product_uom_qty
            out_move.move_line_ids[-1:].qty_done = out_move.move_line_ids[-1:].product_uom_qty + diff
        res = picking.button_validate()
        if res is not True:
            if res['res_model'] == 'stock.immediate.transfer':
                self.env['stock.immediate.transfer'].with_context(res.get('context', {})).create({}).process()
            elif res['res_model'] == 'stock.backorder.confirmation':
                self.env['stock.backorder.confirmation'].with_context(res.get('context', {})).process()
        return out_move

    def _make_in_return(self, move, quantity_to_return):
        stock_return_picking = Form(self.env['stock.return.picking']\
            .with_context(active_ids=[move.picking_id.id], active_id=move.picking_id.id, active_model='stock.picking'))
        stock_return_picking = stock_return_picking.save()
        stock_return_picking.product_return_moves.quantity = quantity_to_return
        stock_return_picking_action = stock_return_picking.create_returns()
        return_pick = self.env['stock.picking'].browse(stock_return_picking_action['res_id'])
        return_pick.move_lines[0].move_line_ids[0].qty_done = quantity_to_return
        return_pick._action_done()
        return return_pick.move_lines

    def _make_out_return(self, move, quantity_to_return):
        stock_return_picking = Form(self.env['stock.return.picking']\
            .with_context(active_ids=[move.picking_id.id], active_id=move.picking_id.id, active_model='stock.picking'))
        stock_return_picking = stock_return_picking.save()
        stock_return_picking.product_return_moves.quantity = quantity_to_return
        stock_return_picking_action = stock_return_picking.create_returns()
        return_pick = self.env['stock.picking'].browse(stock_return_picking_action['res_id'])
        return_pick.move_lines.move_line_ids.qty_done = quantity_to_return
        return_pick.move_lines.move_line_ids.lot_id = move.move_line_ids.lot_id.id
        return_pick._action_done()
        return return_pick.move_lines

    def _make_dropship_move(self, product, quantity, unit_cost, lot_id):
        dropshipped = self.env['stock.move'].create({
            'name': 'dropship %s units' % str(quantity),
            'product_id': product.id,
            'location_id': self.supplier_location.id,
            'location_dest_id': self.customer_location.id,
            'product_uom': self.uom_unit.id,
            'product_uom_qty': quantity,
            'picking_type_id': self.picking_type_out.id,
        })
        if unit_cost:
            dropshipped.price_unit = unit_cost
        dropshipped._action_confirm()
        dropshipped._action_assign()
        dropshipped.move_line_ids.lot_id = lot_id
        dropshipped.move_line_ids.qty_done = quantity
        dropshipped._action_done()
        return dropshipped
