from odoo import api, models


class MrpProduction(models.Model):
    _name = 'mrp.production'
    _inherit = ['mrp.production', 'barcodes.barcode_events_mixin']

    def action_toggle_is_locked1(self):
        return self.action_toggle_is_locked()

    def action_toggle_is_locked2(self):
        return self.action_toggle_is_locked()

    def open_produce_product1(self):
        return self.open_produce_product()

    def open_produce_product2(self):
        return self.open_produce_product()
