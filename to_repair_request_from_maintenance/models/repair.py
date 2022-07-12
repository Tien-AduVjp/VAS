from odoo import api, models, fields

class Repair(models.Model):
    _inherit = 'repair.order'

    maintenance_request_id = fields.Many2one('maintenance.request', string='Maintenance Request',
                                             readonly=True, states={'draft': [('readonly', False)]})

    @api.onchange('product_id')
    def onchange_product_id(self):
        super(Repair, self).onchange_product_id()
        if self.maintenance_request_id:
            lot_id = self.maintenance_request_id.equipment_id.lot_id
            if lot_id.product_id == self.product_id or not self.product_id:
                self.lot_id = lot_id

    @api.onchange('maintenance_request_id')
    def _onchange_maintenance_request_id(self):
        if self.maintenance_request_id:
            if self.maintenance_request_id.equipment_id.product_id:
                self.product_id = self.maintenance_request_id.equipment_id.product_id
                self.product_uom = self.maintenance_request_id.equipment_id.product_id.uom_id
            self.lot_id = self.maintenance_request_id.equipment_id.lot_id
