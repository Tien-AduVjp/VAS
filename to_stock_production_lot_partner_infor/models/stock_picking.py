from odoo import models


class Picking(models.Model):
    _inherit = 'stock.picking'

    def button_validate(self):
        res = super(Picking, self).button_validate()
        move_line_ids = self.mapped('move_line_ids').filtered(lambda l: l.lot_id)

        for line in move_line_ids:
            update_data = {}
            if line.location_id.usage == 'supplier' and line.location_dest_id.usage == 'customer':
                update_data.update({
                    'supplier_id': line.picking_id.partner_id.id,
                    'customer_id': line.picking_id.partner_id.id,
                    })
            elif line.location_id.usage == 'supplier':
                update_data.update({
                    'supplier_id': line.picking_id.partner_id.id,
                    })
            elif line.location_dest_id.usage == 'customer':
                update_data.update({
                    'customer_id': line.picking_id.partner_id.id,
                    'country_state_id': line.picking_id.partner_id.state_id.id,
                    })

            if bool(update_data):
                line.lot_id.write(update_data)
        return res
