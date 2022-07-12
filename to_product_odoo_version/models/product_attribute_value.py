from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from distutils.version import StrictVersion


class ProductAttributeValue(models.Model):
    _inherit = 'product.attribute.value'

    odoo_version_ids = fields.One2many('odoo.version', 'product_attribute_value_id', string='Odoo Versions', readonly=True,
                                       help="Technical field to help compute the sole Odoo version of this attribute value."
                                       " This field never stores more than one Odoo Version")
    odoo_version_id = fields.Many2one('odoo.version', string='Odoo Version', compute='_compute_odoo_version_id', store=True, index=True)

    @api.constrains('attribute_id', 'name')
    def _constrains_name_odoo_version(self):
        product_attribute_odoo_version_id = self.env.ref('to_product_odoo_version.product_attribute_odoo_version')
        for r in self:
            if r.attribute_id.id == product_attribute_odoo_version_id.id:
                try:
                    StrictVersion(r.name)
                except ValueError:
                    raise ValidationError(_("Invalid version number %s. The version should be in the form of either 'x.y' or 'x.y.z'"
                                            " where the x, y, z must be digits.") % r.name)

    @api.depends('odoo_version_ids')
    def _compute_odoo_version_id(self):
        for r in self:
            r.odoo_version_id = r.odoo_version_ids[:1]

    def _prepare_odoo_version_data(self):
        return {
            'name': self.name,
            'product_attribute_value_id': self.id,
            'release_date': fields.Date.today()
            }

    def _create_if_not_exists_odoo_version(self):
        OdooVersion = self.env['odoo.version']
        odoo_version_id = OdooVersion.search([('name', '=', self.name)], limit=1)
        if not odoo_version_id:
            odoo_version_id = OdooVersion.create(self._prepare_odoo_version_data())
        return odoo_version_id

    @api.model_create_multi
    def create(self, vals_list):
        records = super(ProductAttributeValue, self).create(vals_list)
        product_attribute_odoo_version_id = self.env.ref('to_product_odoo_version.product_attribute_odoo_version')
        for rec in records:
            if product_attribute_odoo_version_id == rec.attribute_id:
                odoo_version_id = rec._create_if_not_exists_odoo_version()
                rec.write({
                    'odoo_version_ids': [(4, odoo_version_id.id)]
                    })
        return records

    def write(self, vals):
        product_attribute_odoo_version_id = self.env.ref('to_product_odoo_version.product_attribute_odoo_version')
        if 'attribute_id' in vals:
            for r in self:
                if vals['attribute_id'] != r.attribute_id.id and r.attribute_id.id == product_attribute_odoo_version_id.id:
                    raise UserError(_("The product attribute value %s that represents an Odoo version is not allowed to get modified after creation")
                                    % r.name)
        res = super(ProductAttributeValue, self).write(vals)
        if 'name' in vals:
            odoo_version_ids = self.mapped('odoo_version_id').filtered(lambda v: v.name != vals['name'])
            if odoo_version_ids:
                odoo_version_ids.write({
                    'name': vals['name']
                    })
        return res

    def unlink(self):
        odoo_version_ids = self.mapped('odoo_version_ids')
        res = super(ProductAttributeValue, self).unlink()
        if odoo_version_ids:
            odoo_version_ids.unlink()
        return res
