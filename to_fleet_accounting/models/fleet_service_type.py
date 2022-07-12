from odoo import models, fields, api


class FleetServiceType(models.Model):
    _inherit = 'fleet.service.type'

    product_id = fields.Many2one('product.product', string='Invoiceable Product',
                                 help="The product to be used when invoicing vehicle services of this service type")

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.name = self.product_id.name

    def _prepare_product_vals(self, product_categ=None):
        self.ensure_one()
        product_categ = product_categ or self.env.ref('to_fleet_accounting.cat_vehicle_expense')
        return {
            'name': self.display_name,
            'categ_id': product_categ.id,
            'type': 'service',
            }

    def _generate_product_if_not_exists(self):
        Product = self.env['product.product'].sudo()
        product_categ = self.env.ref('to_fleet_accounting.cat_vehicle_expense')
        for r in self.filtered(lambda t: not t.product_id):
            product = Product.search([('name', 'ilike', '%' + r.name + '%')], limit=1)
            if not product:
                product = Product.create(r._prepare_product_vals(product_categ))
            if not product.categ_id or product.categ_id != product_categ:
                product.categ_id = product_categ.id
            r.product_id = product.id
        return True

    @api.model_create_multi
    def create(self, vals_list):
        records = super(FleetServiceType, self).create(vals_list)
        records._generate_product_if_not_exists()
        return records
