from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_is_zero, float_compare


class StockMove(models.Model):
    _inherit = 'stock.move'

    asset_category_id = fields.Many2one('account.asset.category',
                                        string='Asset Category',
                                        compute='_compute_asset_category_id',
                                        store=True,
                                        readonly=False,
                                        help="If set, it will automatically generate the corresponding assets."
                                        )

    @api.depends('product_id', 'picking_id.location_dest_id', 'location_dest_id', 'picking_code')
    def _compute_asset_category_id(self):
        for r in self:
            if (r.picking_id.location_dest_id.usage == 'asset_allocation'\
                or r.location_dest_id.usage == 'asset_allocation'\
                ) and r.product_id.asset_category_id:
                if not r.asset_category_id:
                    r.asset_category_id = r.product_id.asset_category_id
                else:
                    r.asset_category_id = r.asset_category_id
            else:
                r.asset_category_id = False

    def _prepare_account_asset_val(self, lot_id, value):
        self.ensure_one()
        if lot_id.product_id.tracking == 'none':
            raise UserError(_("Only supports products tracked by a Lot/Serial number!"))

        manual_validate_date_time = self._context.get('manual_validate_date_time', False)
        date = fields.Datetime.to_datetime(manual_validate_date_time) if manual_validate_date_time else self.date
        date = fields.Date.context_today(self, date)
        asset_category_id = self.asset_category_id
        vals = self.env['account.asset.asset'].onchange_category_id_values(asset_category_id.id)['value']
        vals.update({
            'production_lot_id': lot_id.id,
            'name': '%s/%s' % (lot_id.product_id.name, lot_id.name),
            'value': abs(value),
            'category_id': asset_category_id.id,
            'date': date,
            })

        if asset_category_id.date_first_depreciation == 'manual':
            vals.update({
            'first_depreciation_date': date,
            })

        return vals

    def _get_accounting_data_for_valuation(self):
        """ Return the accounts and journal to use to post Journal Entries for
        the real-time valuation of the quant. """
        self.ensure_one()
        journal_id, acc_src, acc_dest, acc_valuation = super(StockMove, self)._get_accounting_data_for_valuation()
        asset_obj = self.env['account.asset.asset']

        # Return a stock picking that contains assets that is in draft state
        if self.location_id.usage == 'asset_allocation' and self._is_in() and self.origin_returned_move_id:
            for line in self.origin_returned_move_id.move_line_ids.filtered(lambda l: l.account_asset_asset_id):
                asset_obj |= line.account_asset_asset_id
            if asset_obj:
                acc_src = asset_obj.category_id.asset_account_id[0].id
                asset_obj.with_context(return_picking=True).unlink()

        if self.location_dest_id.usage == 'asset_allocation':
            if self._is_in():
                # Return a stock picking that contains assets that is in draft state
                if self.origin_returned_move_id and self.origin_returned_move_id.move_line_ids.account_asset_asset_id:
                    acc_src = self.origin_returned_move_id.move_line_ids.account_asset_asset_id.category_id.asset_account_id[0].id
                # Stock in a asset
                if self._context.get('stock_in', False):
                    stock_input_account_id = asset_obj.stock_input_account_id.id or asset_obj.category_id.stock_input_account_id.id
                    if not stock_input_account_id:
                        raise UserError(_("The following field on Asset Category or on Asset is invalid: Stock Input Account"))
                    acc_valuation = stock_input_account_id

            elif self._is_out():
                if self._context.get('sell', False):
                    pass
                elif self._context.get('dispose', False):
                    pass
                else:
                    # Create assets when validating a stock picking
                    asset_category_id = self.asset_category_id
                    if not asset_category_id:
                        raise UserError(_("The following field on Product is invalid: Asset Category"))
                    acc_dest = asset_category_id.asset_account_id.id

        return journal_id, acc_src, acc_dest, acc_valuation

    def _prepare_account_move_line(self, qty, cost, credit_account_id, debit_account_id, description):
        """
        Generate the account.move.line values to post to track the stock valuation difference due to the
        processing of the given quant.
        """
        self.ensure_one()

        if self.location_dest_id.usage == 'asset_allocation':
            res = []
            # To avoid to create dubplicated entries that call from svl.stock_move_id._account_entry_move()
            if self.account_move_ids:
                return res

            valuation_partner_id = self._get_partner_id_for_valuation_lines()

            move_lines_with_asset = self.env['stock.move.line'].search([('id', 'not in', self.move_line_ids.ids), ('lot_id', 'in', self.move_line_ids.lot_id.ids)]) \
                                                    .filtered(lambda line: line.location_id.usage == 'asset_allocation' and line.account_asset_asset_id)

            asset_category_id = self.asset_category_id
            if not asset_category_id:
                raise UserError(_('The following field on Product is invalid: Asset Type'))

            for line in self.move_line_ids:
                description_with_serial = description + ' - %s' % line.lot_id.name

                debit_value = line.account_asset_asset_id.value
                qty = line.qty_done if self._is_in() else -1 * line.qty_done
                for line_with_asset in move_lines_with_asset:
                    if line.lot_id in line_with_asset.lot_id:
                        acc_dest = asset_category_id.asset_account_id.id
                        asset_id = line_with_asset.account_asset_asset_id
                        acc_valuation = asset_id.stock_input_account_id.id or asset_id.category_id.stock_input_account_id.id
                        if not acc_valuation:
                            raise UserError(_("The following field on Asset Category or on Asset is invalid: Stock Input Account"))

                        vals = self._generate_valuation_lines_data(valuation_partner_id, qty, debit_value, debit_value, acc_dest, acc_valuation, description_with_serial).values()
                        res.extend([v for v in vals])
                        move_lines_with_asset -= line_with_asset
                        break
                else:
                    credit_account = line.product_id.product_tmpl_id.get_product_accounts().get('stock_valuation', False)
                    if not credit_account:
                        raise UserError(_("You don't have any stock valuation account defined on your product category. You must define one before processing this operation."))

                    vals = self._generate_valuation_lines_data(valuation_partner_id, qty, debit_value, debit_value, debit_account_id, credit_account.id, description_with_serial).values()
                    res.extend([v for v in vals])

            if res:
                return [(0, 0, line_vals) for line_vals in res]

        return super(StockMove, self)._prepare_account_move_line(qty, cost, credit_account_id, debit_account_id, description)

    def _get_price_unit(self):
        """Returns the unit price to value this stock move """
        for line in self.move_line_ids:
            if line.sudo().account_asset_asset_id:
                location_dest_id, location_id = line.account_asset_asset_id._get_locations()
                location_id = location_id or self.env.ref('to_stock_asset.stock_location_asset').id
                if location_id == line.location_id.id:
                    return self.price_unit
        return super(StockMove, self)._get_price_unit()

    def _account_entry_move(self, qty, description, svl_id, cost):
        """ Accounting Valuation Entries """
        self.ensure_one()
        if self.location_id.usage == 'asset_allocation' and not self.origin_returned_move_id:
            return False
        return super(StockMove, self)._account_entry_move(qty, description, svl_id, cost)

    def _create_out_svl(self, forced_quantity=None):
        """Create a `stock.valuation.layer` from `self`.

        :param forced_quantity: under some circunstances, the quantity to value is different than
            the initial demand of the move (Default value = None)
        """
        if self and self[0].location_dest_id.usage == 'asset_allocation':
            asset_obj = self.env['account.asset.asset']
            svl_vals_list = []

            for move in self:
                move = move.with_company(move.company_id)
                valued_move_lines = move._get_out_move_lines()
                valued_quantity = 0
                for valued_move_line in valued_move_lines:
                    valued_quantity += valued_move_line.product_uom_id._compute_quantity(valued_move_line.qty_done, move.product_id.uom_id)
                if float_is_zero(forced_quantity or valued_quantity, precision_rounding=move.product_id.uom_id.rounding):
                    continue
                for line in move.move_line_ids:
                    qty = forced_quantity or line.product_uom_id._compute_quantity(line.qty_done, move.product_id.uom_id)
                    svl_vals = move.product_id.with_context(lot_id=line.lot_id.id)._prepare_out_svl_vals(qty, move.company_id)
                    svl_vals.update(move._prepare_common_svl_vals())
                    if forced_quantity:
                        svl_vals['description'] = "Correction of %s (modification of past move)" % move.picking_id.name or move.name
                    svl_vals_list.append(svl_vals)

                    can_read = self.env['account.asset.asset'].check_access_rights('write', False)
                    asset_obj = asset_obj if can_read else asset_obj.sudo()
                    asset_obj = asset_obj.create(move._prepare_account_asset_val(line.lot_id, svl_vals['value']))
                    line.write({
                        'account_asset_asset_id': asset_obj.id,
                        })

            return self.env['stock.valuation.layer'].sudo().create(svl_vals_list)

        return super(StockMove, self)._create_out_svl(forced_quantity=forced_quantity)
