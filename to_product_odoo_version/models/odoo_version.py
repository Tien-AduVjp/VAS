from odoo import models, fields, api


class OdooVersion(models.Model):
    _inherit = 'odoo.version'

    product_attribute_value_id = fields.Many2one('product.attribute.value', string='Product Attribute Value', index=True, readonly=True)

    _sql_constraints = [
        ('product_attribute_value_id_unique',
         'UNIQUE(product_attribute_value_id)',
         "The Product Attribute Value must be unique! You must not have two or more Odoo versions refer to the same Product Attribute Value."),
    ]

    def _prepare_product_attribute_value_data(self):
        return {
            'name': self.name,
            'attribute_id': self.env.ref('to_product_odoo_version.product_attribute_odoo_version').id
            }

    def _create_if_not_exists_product_attribute_value(self):
        ProductAttributeValue = self.env['product.attribute.value']
        attr_val_id = ProductAttributeValue.search([('name', '=', self.name)], limit=1)
        if not attr_val_id:
            attr_val_id = ProductAttributeValue.sudo().create(self._prepare_product_attribute_value_data())
        return attr_val_id

    @api.model_create_multi
    def create(self, vals_list):
        records = super(OdooVersion, self).create(vals_list)
        for record in records:
            if not record.product_attribute_value_id:
                record.write({'product_attribute_value_id': record._create_if_not_exists_product_attribute_value().id})
        return records

    def write(self, vals):
        res = super(OdooVersion, self).write(vals)
        if 'name' in vals:
            product_attribute_value_ids = self.mapped('product_attribute_value_id').sudo().filtered(lambda attr_val: attr_val.name != vals['name'])
            if product_attribute_value_ids:
                product_attribute_value_ids.write({
                    'name':vals['name']
                    })
        return res

    def unlink(self):
        product_attribute_value_ids = self.mapped('product_attribute_value_id').sudo()
        res = super(OdooVersion, self).unlink()
        if product_attribute_value_ids:
            product_attribute_value_ids.unlink()
        return res

