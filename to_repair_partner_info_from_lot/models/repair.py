from odoo import  models, api


class Repair(models.Model):
    _inherit = 'repair.order'
    
    @api.onchange('lot_id')
    def _onchange_location_id(self):
        if self.state == 'draft':
            if self.lot_id.customer_id:
                self.partner_id = self.lot_id.customer_id
            else:
                self.partner_id = False
