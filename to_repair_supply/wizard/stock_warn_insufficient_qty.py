from odoo import fields, models, api


class StockWarnInsufficientQtyRepair(models.TransientModel):
    _inherit = 'stock.warn.insufficient.qty.repair'

    repair_id = fields.Many2one('repair.order', string='Repair')
    src_location_id = fields.Many2one('stock.location', string='Current Location', required=True)

    def action_done(self):
        self.ensure_one()
        self.repair_id._generate_moves(self.src_location_id)
        return self.repair_id.action_repair_confirm()

    @api.onchange('quant_ids')
    def _onchange_quant_ids(self):
        if self.quant_ids:
            self.src_location_id = self.quant_ids[0].location_id
