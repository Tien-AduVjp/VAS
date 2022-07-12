from odoo import fields, models


class PurchaseRequisition(models.Model):
    _inherit = 'purchase.requisition'
    
    def _get_picking_in(self):
        pick_in = super(PurchaseRequisition, self)._get_picking_in()
        if pick_in.sudo().warehouse_id.access_user_ids and self.env.user.id not in pick_in.sudo().warehouse_id.access_user_ids.ids:
            company = self.env.company
            pick_in = self.env['stock.picking.type'].search(
                [('warehouse_id.company_id', '=', company.id), ('code', '=', 'incoming')],
                limit=1
            )
        return pick_in
    
    picking_type_id = fields.Many2one(default=_get_picking_in)
