from odoo import models, fields


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    def _prepare_equipment_data(self):
        data = super(StockMoveLine, self)._prepare_equipment_data()
        if self.lot_id:
            data['effective_date'] = fields.Date.today()
        if self.product_id:
            equipment_working_frequency_data = []
            for template in self.product_id.working_frequency_template_ids:
                equipment_working_frequency_data.append((0, 0, template._prepare_equipment_working_frequency_data()))
            if equipment_working_frequency_data:
                data['equipment_working_frequency_ids'] = equipment_working_frequency_data
        return data

    def _action_done(self):
        super(StockMoveLine, self)._action_done()
        self.exists().filtered(lambda l: l.lot_id and l.lot_id.equipment_id).mapped('lot_id.equipment_id').write({
            'effective_date':fields.Date.today()
            })
