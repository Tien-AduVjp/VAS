from odoo import models, api, _
from odoo.exceptions import ValidationError


class StockWarehouse(models.Model):
    _inherit = 'stock.warehouse'

    @api.constrains('view_location_id')
    def _check_view_location_id(self):
        for r in self:
            overlapping = self.search([('id', '!=', r.id), ('view_location_id', '=', r.view_location_id.id)], limit=1)
            if overlapping:
                raise ValidationError(_("You cannot set the location '%s' as the view location for this warehouse since the location"
                                        " is being used as the view location for the warehouse '%s'") % (r.view_location_id.name, overlapping.name))

