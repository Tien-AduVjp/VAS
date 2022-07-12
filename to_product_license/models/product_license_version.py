from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from distutils.version import StrictVersion


class ProductLicenseVersion(models.Model):
    _name = 'product.license.version'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'License Version'
    _order = 'date_released desc, name desc'

    name = fields.Char(string='Version', required=True, tracking=True)
    short_name = fields.Char(string='Short Name', help="The short name of the license version that help identify the license version")
    image = fields.Binary(string='Icon Image')
    active = fields.Boolean('Active', default=True, help="If unchecked, it will allow you to hide the license version without removing it.")
    date_released = fields.Date(string='Date Released', required=True, tracking=True)
    license_id = fields.Many2one('product.license', string='License', required=True, ondelete='cascade', tracking=True)
    content = fields.Html(string='Content', translate=True, tracking=True, help="The content of the license version")
    ref_url = fields.Char(string='Ref. URL', tracking=True)
    product_ids = fields.Many2many('product.product', 'product_product_product_license_version_rel', 'product_license_version_id', 'product_id', string='Product',
                                   readonly=True, help="The products that are assigned with this license version")
    products_count = fields.Integer(string='Products Count', compute='_compute_products_count', store=True)

    _sql_constraints = [
        ('name_license_id_unique',
         'UNIQUE(name, license_id)',
         "Branch version must be unique per license!"),
    ]

    @api.depends('product_ids')
    def _compute_products_count(self):
        for r in self:
            r.products_count = len(r.product_ids)

    @api.constrains('name')
    def _validate_version_string(self):
        for r in self:
            try:
                StrictVersion(r.name)
            except ValueError:
                raise ValidationError(_("Invalid version number %s. The version should be in the form of either 'x.y' or'x.y.z'"
                                        " where the x, y, z must be digits.") % r.name)

    def name_get(self):
        result = []
        for r in self:
            if r.license_id:
                result.append((r.id, '%s [%s] - %s%s' % (r.license_id.name, r.license_id.short_name, _('v'), r.name)))
            else:
                result.append((r.id, r.name))
        return result

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = ['|', '|', ('license_id.name', '=ilike', name + '%'), ('license_id.short_name', '=ilike', name + '%'), ('name', operator, name)]
        recs = self.search(domain + args, limit=limit)
        return recs.name_get()

    def action_view_products(self):
        product_ids = self.mapped('product_ids')

        action = self.env.ref('product.product_normal_action')
        result = action.read()[0]

        # choose the view_mode accordingly
        products_count = len(product_ids)
        if products_count != 1:
            result['domain'] = "[('id', 'in', " + str(product_ids.ids) + ")]"
        elif products_count == 1:
            res = self.env.ref('product.product_normal_form_view', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = product_ids.id
        return result

    def write(self, vals):
        for r in self:
            if r.product_ids and 'license_id' in vals:
                raise ValidationError(_("You may not be able to change the license of the version '%s' while there is a product being refer to the license version")
                                      % r.display_name)
        return super(ProductLicenseVersion, self).write(vals)
