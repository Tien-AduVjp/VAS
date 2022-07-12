from odoo import fields, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    def _set_backdate(self, backdate):
        """
        set backdate for done stock moves and their conresponding done stock move lines
        """
        self.filtered(lambda x: x.state == 'done').write({'date': backdate})
        move_line_ids = self.mapped('move_line_ids').filtered(lambda x: x.state == 'done')
        if move_line_ids:
            move_line_ids.write({'date': backdate})

    def _action_done(self, cancel_backorder=False):
        manual_validate_date_time = self._context.get('manual_validate_date_time', False)
        if manual_validate_date_time:
            force_period_date = self._context.get('force_period_date', False) or fields.Date.context_today(self, fields.Datetime.to_datetime(manual_validate_date_time))
            res = super(StockMove, self.with_context(force_period_date=force_period_date))._action_done(cancel_backorder)
            self._set_backdate(manual_validate_date_time)
            return res
        return super(StockMove, self)._action_done(cancel_backorder)
