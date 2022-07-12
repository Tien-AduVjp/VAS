from odoo import models, fields


class OdooModuleVersionImage(models.Model):
    _name = 'odoo.module.version.image'
    _description = 'Odoo Module Version Image'

    name = fields.Char('Name')
    image = fields.Binary('Image', attachment=True)
    filename = fields.Char(string='File Name', help="Technical field for forming the file name of the Image")
    module_version_id = fields.Many2one('odoo.module.version', string='Related Odoo Module Version', copy=True, index=True)
    product_id = fields.Many2one('product.product', related='module_version_id.product_id', store=True, index=True, readonly=True)
    product_tmpl_id = fields.Many2one('product.template', related='module_version_id.product_tmpl_id', store=True, index=True, readonly=True)
