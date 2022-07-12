from odoo import models, fields, api


class PickingType(models.Model):
    _inherit = 'stock.picking.type'

    can_create_equipment = fields.Boolean(string="Can create equipment")

    @api.model
    def _update_buy_picking_types(self):
        """
        This method to be called by XML to update all the existing buy picking types to allow creation of equipments
        """
        picking_type_ids = self.env['stock.picking.type'].search([('code', '=', 'incoming')])
        picking_type_ids.write({'can_create_equipment': True})
