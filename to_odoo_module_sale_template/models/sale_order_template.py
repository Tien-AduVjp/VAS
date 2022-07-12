from odoo import api, fields, models
from odoo.models import NewId


class SaleOrderTemplate(models.Model):
    _inherit = "sale.order.template"

    @api.model
    def _default_odoo_version(self):
        return self.env['odoo.version'].search([], limit=1)

    autoload_odoo_apps = fields.Boolean(string='Load Odoo Apps')
    odoo_version_id = fields.Many2one('odoo.version', default=_default_odoo_version)
    ir_module_category_ids = fields.Many2many('ir.module.category', string='App Categories')

    @api.onchange('autoload_odoo_apps', 'odoo_version_id', 'ir_module_category_ids')
    def _onchange_autoload_odoo_apps(self):
        if self.autoload_odoo_apps and self.odoo_version_id:
            existing_line_ids = self.sale_order_template_line_ids

            # cleanup which removes newly added app lines which are not saved in the db yet
            recent_added_line_ids = existing_line_ids.filtered(lambda l: isinstance(l.id, NewId) and not l.id.origin and l.product_id.odoo_module_version_id)
            if recent_added_line_ids:
                existing_line_ids -= recent_added_line_ids

            product_ids = self.env['product.product']

            if self.ir_module_category_ids:
                domain = [
                    ('odoo_module_version_id', '!=', False),
                    ('odoo_module_version_id.odoo_version_id', '=', self.odoo_version_id.id),
                    ('odoo_module_version_id.ir_module_category_id', 'in', self.ir_module_category_ids.ids)]
                product_ids |= self.env['product.product'].search(domain)

            existing_product_ids = existing_line_ids.mapped('product_id')
            if existing_product_ids:
                product_ids -= existing_product_ids

            last_sequence = 0
            for line in existing_line_ids:
                if line.sequence > last_sequence:
                    last_sequence = line.sequence

            for product_id in product_ids:
                last_sequence += 1
                new_line = existing_line_ids.new({
                    'sale_order_template_id': self.id,
                    'product_id': product_id.id,
                    'product_uom_qty': 1.0,
                    'sequence': last_sequence,
                    })
                new_line._onchange_product_id()
                existing_line_ids += new_line

            self.sale_order_template_line_ids = existing_line_ids

