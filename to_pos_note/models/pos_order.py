from odoo import models, api

class PosOrder(models.Model):
    _inherit = 'pos.order'
    
    @api.model
    def _order_fields(self, ui_order):
        fields = super(PosOrder, self)._order_fields(ui_order)
        fields['note'] = ui_order.get('note', '')
        return fields

