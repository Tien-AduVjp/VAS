from odoo import models, _
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def button_validate(self):
        for product in self.move_lines.product_id:
            if product.cost_method == 'specific_identification' and product.tracking == 'none':
                raise UserError(_("Tracking by a lot/serial number must be applied for product '%s' with specific identification costing method!") % product.display_name)
        return super(StockPicking, self).button_validate()
