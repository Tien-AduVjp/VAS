from odoo import models, fields, api
from odoo.tools import float_is_zero


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'
    # check on `invoice_line_id` field. I can't find it anywhere
    odoo_module_version_id = fields.Many2one('odoo.module.version', string='Odoo Module Versions', compute='_compute_odoo_module_version', store=True)
    # because the relationship between account move line and module version is many2one, compute field `odoo_module_versions_count` should not exist
    odoo_app_dependency = fields.Boolean(string='Odoo App Dependencies', help="This field is to indicate that the line is added"
                                         " as a dependency for other lines")

    @api.depends('quantity', 'product_id.odoo_module_version_id')
    def _compute_odoo_module_version(self):
        for r in self:
            r.odoo_module_version_id = r.get_odoo_module_versions()[:1]

    def get_odoo_module_versions(self, uom_precision=None):
        if not uom_precision:
            uom_precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        return self.filtered(lambda l: not float_is_zero(l.quantity, precision_digits=uom_precision)).sudo().mapped('product_id.odoo_module_version_id')
