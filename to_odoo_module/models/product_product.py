import threading

from odoo import models, fields, api, _


class ProductProduct(models.Model):
    _inherit = 'product.product'

    odoo_module_versions_count = fields.Integer(string='Odoo Module Versions Count', compute='_compute_odoo_module_versions_count')
    odoo_module_version_id = fields.Many2one('odoo.module.version', string='Odoo Module Version', index=True, readonly=True,
                                             help="The sole Odoo Module Version of this product")
    is_odoo_app = fields.Boolean(string='Is Odoo App', compute='_compute_is_odoo_app', store=True, copy=False, index=True,
                                 help="This field is to indicate if this product represents Odoo Apps")
    odoo_module_id = fields.Many2one('odoo.module', string='Odoo Module', related='odoo_module_version_id.module_id',
                                     store=True, copy=False, ondelete='set null', readonly=True,
                                     help="The Odoo module that is associated with this product")

    odoo_module_version_image_ids = fields.One2many('odoo.module.version.image', 'product_id', string='Odoo Module Images', copy=False, readonly=True)

    @api.depends('odoo_module_version_id')
    def _compute_is_odoo_app(self):
        for r in self:
            is_odoo_app = False
            if r.odoo_module_version_id:
                is_odoo_app = True
            r.is_odoo_app = is_odoo_app

    def _compute_odoo_module_versions_count(self):
        file_data = self.env['odoo.module.version'].read_group([('product_id', 'in', self.ids)], ['product_id'], ['product_id'])
        mapped_data = dict([(dict_data['product_id'][0], dict_data['product_id_count']) for dict_data in file_data])
        for r in self:
            r.odoo_module_versions_count = mapped_data.get(r.id, 0)

    def action_view_odoo_module_versions(self):
        # TODO: need to improve because one product has only a odoo module version
        odoo_module_versions = self.mapped('odoo_module_version_id')
        action = self.env.ref('to_odoo_module.odoo_module_version_action')
        result = action.read()[0]

        # get rid off the default context
        result['context'] = {}

        # choose the view_mode accordingly
        modules_count = len(odoo_module_versions)
        if modules_count != 1:
            result['domain'] = "[('product_id', 'in', " + str(self.ids) + ")]"
        elif modules_count == 1:
            res = self.env.ref('to_odoo_module.odoo_module_version_form_view', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = odoo_module_versions.id
        return result

    @api.model_create_multi
    def create(self, vals_list):
        technical_name = self._context.get('technical_name', '')
        if technical_name:
            for vals in vals_list:
                vals['default_code'] = technical_name
        return super(ProductProduct, self).create(vals_list)

    def synch_licenses_from_odoo_module_versions(self):
        for r in self:
            update_data = {}
            product_license_versions = r.mapped('odoo_module_version_id.license_version_id')
            if product_license_versions:
                update_data['product_license_version_ids'] = [(6, 0, product_license_versions.ids)]
            elif r.product_license_version_ids:
                update_data['product_license_version_ids'] = [(3, license_id) for license_id in r.product_license_version_ids.ids]
            if bool(update_data):
                r.write(update_data)

    def _get_app_author_for_name(self):
        vendor_name = ""
        if self.odoo_module_version_id:
            if self.odoo_module_version_id.vendor_id:
                vendor_name = self.odoo_module_version_id.vendor_id.name
            elif self.odoo_module_version_id.git_branch_id and self.odoo_module_version_id.git_branch_id.vendor_id:
                vendor_name = self.odoo_module_version_id.git_branch_id.vendor_id.name
        if vendor_name:
            return _("By %s") % vendor_name
        else:
            return ""

    def name_get(self):
        # skip manually method in test mode to avoid error when running unit test of Odoo
        if getattr(threading.currentThread(), 'testing', False) or self.env.registry.in_test_mode():
            return super(ProductProduct, self).name_get()
        # Prefetch the fields used by the `name_get`, so `browse` doesn't fetch other fields
        # Use `load=False` to not call `name_get` for the `product_tmpl_id`
        self.sudo().read(['name', 'default_code', 'product_tmpl_id', 'attribute_line_ids', 'odoo_module_version_id'], load=False)
        res = super(ProductProduct, self).name_get()
        res_dict = dict(res)
        products = self.browse(res_dict.keys())
        for product in products:
            res_dict[product.id] += ' %s' % product.sudo()._get_app_author_for_name()
        res = [(k, v) for k, v in res_dict.items()]
        return res

    def _prepare_app_dependency_line_data(self, quantity_field_name='quantity', sequence=10):
        """
        Hooking method to prepare data for a dependent app invoice line
        """
        return {
            'product_id': self.id,
            'odoo_app_dependency': True,
            quantity_field_name: 1.0,
            'sequence': sequence,
            }

    def get_app_product_dependencies(self, incl_the_current=True):
        """
        Calculating app product dependencies of given products

        :param: bool `include_the_current`: whether or not include the current self

        :context: ResPartner object `partner`: `res.partner` record for calculating their unbought dependencies application products
        :context: bool `exclude_paid_apps`: whether or not should exclude partner paid products (default True)

        :return: Product object `product.product` record
        """
        exclude_paid_apps = self._context.get('exclude_paid_apps', True)
        partner = self._context.get('partner', False)
        Products = self.env['product.product']

        for r in self:
            if r.is_odoo_app:
                dependencies = r._product_app_dependencies(
                    partner=partner,
                    exclude_paid_apps=exclude_paid_apps,
                    incl_the_current=incl_the_current
                )
                Products += dependencies
        if incl_the_current:
            Products |= self

        return Products

    def _product_app_dependencies(self, partner, exclude_paid_apps, incl_the_current=True):
        """
        Hook method to get dependencies of given product to inherit later
        """
        self.ensure_one()
        omv = self.odoo_module_version_id
        if not exclude_paid_apps or not partner:
            dependencies = omv.with_context(exclude_standard_odoo_modules=True).get_recursive_dependencies(incl_the_current=incl_the_current)
        else:
            dependencies = omv.with_context(
                    exclude_standard_odoo_modules=True,
                    partner=partner
                ).get_unbought_recursive_dependencies(incl_the_current=incl_the_current)
        return dependencies.product_id
