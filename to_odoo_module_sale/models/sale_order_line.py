from odoo import models, fields, api
from odoo.tools import float_is_zero


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    odoo_module_version_id = fields.Many2one('odoo.module.version', string='Odoo Module Versions', compute='_compute_odoo_module_version')
    odoo_app_dependency = fields.Boolean(string='Odoo App Dependencies', help="This field is to indicate that the line is added"
                                         " as a dependency for other lines")

    def get_odoo_module_versions(self, uom_precision=None):
        if not uom_precision:
            uom_precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        return self.filtered(lambda l: not float_is_zero(l.product_uom_qty, precision_digits=uom_precision)).sudo().mapped('product_id.odoo_module_version_id')

    def _compute_odoo_module_version(self):
        prec = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        for r in self:
            if not float_is_zero(r.product_uom_qty, precision_digits=prec):
                r.odoo_module_version_id = r.get_odoo_module_versions(prec).id
            else:
                r.odoo_module_version_id = False

    def _get_biggest_sequence(self):
        last_sequence = 0
        for r in self:
            if r.sequence > last_sequence:
                last_sequence = r.sequence
        return last_sequence

