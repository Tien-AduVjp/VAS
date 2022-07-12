from odoo import models, api


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.onchange('can_be_equipment')
    def _onchange_can_be_equipment(self):
        if self.can_be_equipment:
            self.type = 'product'
            self.tracking = 'serial'
        else:
            self.type = self._origin.type or self.type
            self.tracking = self._origin.tracking or self.tracking

    def write(self, vals):
        self.inverse_related_fields(vals)
        return super(ProductProduct, self).write(vals)

    def inverse_related_fields(self, vals):
        """ Inverse records that are not being computed
        to avoid _check_constrain_equipment_tracking contraints.
        """
        inverse_vals = {}
        for key in self._fields_list_to_inverse():
            if key in vals:
                inverse_vals[key] = vals[key]
        # If len(inverse_vals) <=1, Odoo handled it
        if len(inverse_vals) > 1:
            self.product_tmpl_id.write(inverse_vals)

    @api.model
    def _fields_list_to_inverse(self):
        """Return fields list to inverse"""
        return ['can_be_equipment', 'type', 'tracking']
