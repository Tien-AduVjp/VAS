from odoo import fields, models, _


class AdjustmentLines(models.Model):
    _inherit = 'stock.valuation.adjustment.lines'
    
    
    def _create_account_move_line(self, move, credit_account_id, debit_account_id, qty_out, already_out_account_id):
        self.ensure_one()
        AccountMoveLine = []
        lot_ids = self.move_id.move_line_ids.mapped('lot_id')
        stock_move_line_ids = self.env['stock.move.line'].search([
            ('lot_id', 'in', lot_ids.ids), 
            ('account_asset_asset_id', '!=', False)]) \
            .filtered(lambda line: line.location_dest_id.usage == 'asset_allocation').sorted(key='date', reverse=True)
        qty_out_is_asset = 0
        
        # Create account move lines for quants already out of stock
        # If asset state in ['draft', 'open'], put the value of landed cost into the asset value for depreciation
        # Elif asset state in ['sold', 'disposed'], put the value of landed cost into the value of the expense
        # Elif asset state == 'stock_in', put the value of landed cost into the value of stock
        if qty_out > 0 and stock_move_line_ids:
            base_line = {
                'name': self.name,
                'product_id': self.product_id.id,
                'quantity': 0,
                }
            
            for line_included_cost in self.move_id.move_line_ids:
                for line_is_out in stock_move_line_ids:
                    if line_included_cost.lot_id == line_is_out.lot_id:
                        if line_is_out.account_asset_asset_id.state in ['draft', 'open']:
                            asset_account_id = line_is_out.account_asset_asset_id.category_id.asset_account_id.id
                        elif line_is_out.account_asset_asset_id.state in ['sold', 'disposed']:
                            asset_account_id = line_is_out.account_asset_asset_id.depreciation_expense_account_id.id \
                                            or line_is_out.account_asset_asset_id.category_id.depreciation_expense_account_id.id
                        elif line_is_out.account_asset_asset_id.state == 'stock_in':
                            asset_account_id = line_is_out.account_asset_asset_id.stock_input_account_id.id \
                                            or line_is_out.account_asset_asset_id.category_id.stock_input_account_id.id
                        
                        debit_line = dict(base_line, 
                                          name=(self.name + ": " + str(line_is_out.qty_done) + _(' already out')),
                                          quantity=0,
                                          account_id=asset_account_id)
                        credit_line = dict(base_line,
                                           name=(self.name + ": " + str(line_is_out.qty_done) + _(' already out')),
                                           quantity=0,
                                           account_id=debit_account_id)
                        diff = self.additional_landed_cost * line_is_out.qty_done / self.quantity
                        if diff > 0:
                            debit_line['debit'] = diff
                            credit_line['credit'] = diff
                        else:
                            # negative cost, reverse the entry
                            debit_line['credit'] = -diff
                            credit_line['debit'] = -diff
                        AccountMoveLine.append([0, 0, debit_line])
                        AccountMoveLine.append([0, 0, credit_line])

                        # TDE FIXME: oh dear
                        if self.env.company.anglo_saxon_accounting:
                            debit_line = dict(base_line,
                                              name=(self.name + ": " + str(line_is_out.qty_done) + _(' already out')),
                                              quantity=0,
                                              account_id=credit_account_id)
                            credit_line = dict(base_line,
                                               name=(self.name + ": " + str(line_is_out.qty_done) + _(' already out')),
                                               quantity=0,
                                               account_id=asset_account_id)

                            if diff > 0:
                                debit_line['debit'] = diff
                                credit_line['credit'] = diff
                            else:
                                # negative cost, reverse the entry
                                debit_line['credit'] = -diff
                                credit_line['debit'] = -diff
                            AccountMoveLine.append([0, 0, debit_line])
                            AccountMoveLine.append([0, 0, credit_line])
                        
                        if line_is_out.account_asset_asset_id.state in ['draft', 'open']:
                            line_is_out.account_asset_asset_id.write({
                                'value': line_is_out.account_asset_asset_id.value + diff,
                                'value_residual': line_is_out.account_asset_asset_id.value_residual + diff,
                                })
                            line_is_out.account_asset_asset_id._compute_depreciation_board()
                        
                        qty_out_is_asset += line_is_out.qty_done
                        stock_move_line_ids -= stock_move_line_ids.filtered(lambda line: line.lot_id == line_is_out.lot_id)
                        break
        res = super(AdjustmentLines, self)._create_account_move_line(move, credit_account_id, debit_account_id, qty_out-qty_out_is_asset, already_out_account_id)
        return res + AccountMoveLine

