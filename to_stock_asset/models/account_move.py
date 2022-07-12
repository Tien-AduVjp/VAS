from odoo import fields, models, _
from odoo.exceptions import UserError


class AccountMove(models.Model):
    _inherit = 'account.move'


    def action_post(self):
        res = super(AccountMove, self).action_post()

        #Ensure stock move date and stock move line date as account move date
        for r in self:
            asset = r.sudo().account_asset_id
            move_line = asset.stock_move_line_ids.filtered(
                lambda line: line.location_dest_id.usage == 'internal' and line.state not in ('cancel', 'done')
            )
            if asset and move_line:
                move_line_date = fields.Date.context_today(self, move_line.date)
                if move_line_date != r.date:
                    year, month, day = self.env['to.base'].split_date(r.date)
                    date = move_line.date.replace(year=year, month=month, day=day)
                    move_line.move_id.write({
                        'date': date,
                        'move_line_ids': [(1, move_line.id, {'date': date})],
                        })
        return res

    def _post(self, soft=True):
        # Check account move date that cannot be set before purchase date/stock input date!
        lot_ids = self.sudo().mapped('asset_depreciation_ids.asset_id.production_lot_id')
        if lot_ids:
            move_lines = self.env['stock.move.line'].search([('state', '=', 'done'), ('lot_id', 'in', lot_ids.ids)]) \
                .filtered(lambda line: line.state not in ('cancel', 'done') and line.location_dest_id.usage == 'internal')
            move_lines.read(['date'])
            if move_lines:
                for move in self:
                    lot = move.mapped('asset_depreciation_ids.asset_id.production_lot_id')
                    dates = move_lines.filtered(lambda line: line.lot_id == lot and line.id not in move.stock_move_id.move_line_ids.ids).mapped('date')
                    if dates:
                        date = max(dates).date()
                        if date > move.date:
                            raise UserError(_("The date cannot be set before purchase date/stock input date!"))

        res = super(AccountMove, self)._post(soft=soft)

        #Ensure stock move date and stock move line date as account move date
        for move in self:
            stock_move_id = move.stock_move_id
            if stock_move_id.move_line_ids and stock_move_id.move_line_ids[0].sudo().account_asset_asset_id \
                                                and stock_move_id.state not in ['cancel', 'done']:
                date = stock_move_id.date
                stock_move_id._action_done(cancel_backorder=False)
                if move.date != stock_move_id.date:
                    year, month, day = self.env['to.base'].split_date(move.date)
                    date = date.replace(year=year, month=month, day=day)
                    stock_move_id.write({
                        'date': date,
                        'move_line_ids': [(1, line.id, {'date': date}) for line in stock_move_id.move_line_ids],
                        })
        return res

    def unlink(self):
        move_ids = self.mapped('stock_move_id').filtered(lambda move: move.move_line_ids and move.move_line_ids[0].sudo().account_asset_asset_id \
                                        and move.state not in ['cancel', 'done'])
        move_ids._action_cancel()

        return super(AccountMove, self).unlink()
