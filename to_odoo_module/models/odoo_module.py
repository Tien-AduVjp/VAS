from base64 import b64decode

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class OdooModule(models.Model):
    _name = 'odoo.module'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'image.mixin']
    _description = 'Odoo Module'

    name = fields.Char(name='Name', translate=True, compute='_compute_name', inverse='_set_name', store=True, index=True)
    technical_name = fields.Char(string='Technical Name', required=True, index=True)

    product_tmpl_id = fields.Many2one('product.template', string='Product Template', index=True,
                                       help="The product template for which this module presents for accounting integration."
                                       " Do not fill it if you don't sell this module (e.g. an Odoo standard module)")
    odoo_module_version_ids = fields.One2many('odoo.module.version', 'module_id', string='Odoo Module Versions', auto_join=True)
    odoo_module_versions_count = fields.Integer(string='Odoo Module Versions Count', compute='_compute_odoo_module_versions_count')
    odoo_version_ids = fields.Many2many('odoo.version', 'odoo_module_odoo_version_rel', 'module_id', 'version_id', string='Odoo Versions',
                                        compute='_compute_odoo_versions', store=True,
                                        help="The Odoo versions supported by this module."
                                        " The versions here is automatically computed based on the module versions' Odoo versions related to this module")
    odoo_module_version_id = fields.Many2one('odoo.module.version', string='Latest Version', compute='_compute_odoo_module_version_id', store=True, index=True)
    summary = fields.Text(string='Summary', translate=True, compute='_compute_summary', inverse='_set_summary', store=True)
    description = fields.Text(string='Description', translate=True, compute='_compute_description', inverse='_set_description', store=True)
    description_html = fields.Html('Description HTML', compute='_get_desc')
    git_repository_ids = fields.Many2many('git.repository', 'git_repo_odoo_module_rel', 'odoo_module_id', 'git_repository_id', string='Git Repositories',
                                       readonly=True)
    git_repository_id = fields.Many2one('git.repository', string='Git Repository', compute='_compute_git_repository_id', inverse='_inverse_git_repository_id', store=True, index=True)
    price_currency = fields.Monetary(related='odoo_module_version_id.price_currency')
    currency_id = fields.Many2one(related='odoo_module_version_id.currency_id')
    price = fields.Monetary(related='odoo_module_version_id.price')
    company_currency_id = fields.Many2one(related='odoo_module_version_id.company_currency_id', string='Company Currency')
    license_version_ids = fields.Many2many('product.license.version', string='Licenses', compute='_compute_license_versions')
    total_downloads_count = fields.Integer(string='Total Downloads', compute='_compute_downloads_count',
                                           help="The total downloads count of all the version of this module")
    external_downloads_count = fields.Integer(string="External Downloads", compute="_compute_external_downloads_count",
                                              help="The external downloads count of all the version of this module")
    
    active = fields.Boolean(
        'Active', default=True,
        help="If unchecked, it will allow you to hide the odoo module without removing it.")

    @api.model
    def _identical_images(self, img1, img2):
        """
        This function compare 2 images in PIL supported file type and .svg file type

        :param: img1: b64encode binary string of image
        :param: img2: b64encode binary string of image

        :return: True if 2 are identical or both not in [PIL supported types + .svg]
                 False if 2 are not indentical or not in same file types

        :rtype: Boolean
        """
        try:
            return self.env['to.base'].identical_images(img1, img2)
        except Exception:
            # OSError raise when img1 or img2 is not pillow supported types
            # b64decode 2 images, if 2 are both .svg files, compare binary string
            # else (1 is .svg file and 1 is not): return False (update new image)
            img1 = b64decode(img1)
            img2 = b64decode(img2)
            if b'<svg' in img1 and b'/svg>' in img1 and b'<svg' in img2 and b'/svg>' in img2:
                return img1 == img2
            else:
                return False

    def toggle_active(self):
        super(OdooModule, self).toggle_active()
        if not self._context.get('ignore_toggle_versions', False):
            self.mapped('odoo_module_version_id').filtered(lambda v: v.active != v.module_id.active).toggle_active()

    @api.constrains('git_repository_ids')
    def _check_git_repositories(self):
        for r in self:
            if len(r.git_repository_ids) > 1:
                raise ValidationError(_("A Module cannot belong to more than one git repository"))

    @api.depends('git_repository_ids')
    def _compute_git_repository_id(self):
        for r in self:
            r.git_repository_id = r.git_repository_ids[0] if r.git_repository_ids else False

    def _inverse_git_repository_id(self):
        pass

    def _compute_downloads_count(self):
        download_stat_data = self.env['odoo.module.version.download.stat'].read_group(
            [('odoo_module_id', 'in', self.ids)],
            ['odoo_module_id'],
            ['odoo_module_id'])
        mapped_data = dict([(download_stat['odoo_module_id'][0], download_stat['odoo_module_id_count']) for download_stat in download_stat_data])
        for r in self:
            r.total_downloads_count = mapped_data.get(r.id, 0)
            
    def _compute_external_downloads_count(self):
        product_tmpls = self.mapped("product_tmpl_id")
        if product_tmpls:
            product_tmpls.read(["odoo_module_version_ids", "odoo_module_id"])
        for r in self:
            r.external_downloads_count = sum(product_tmpls.filtered(lambda product_tmpl:product_tmpl.odoo_module_id == r).mapped("odoo_module_version_ids.external_downloads_count"))

    @api.depends('product_tmpl_id')
    def _check_unique_product_tmpl(self):
        for r in self:
            if r.product_tmpl_id:
                existing = self.search([('id', '!=', r.id), ('product_tmpl_id', '=', r.product_tmpl_id.id)], limit=1)
                if existing:
                    raise ValidationError(_("The Odoo Module %s is trying to create relation with the product template %s which is already in"
                                            " relation with the Odoo Module %s")
                                            % (r.display_name, r.product_tmpl_id.name, existing.display_name))

    def _compute_license_versions(self):
        for r in self:
            r.license_version_ids = r.odoo_module_version_ids.mapped('license_version_id')

    def get_latest_version(self):
        """
        Get the latest Odoo Module Version, the one have bigest value in full_version_str
        @return: odoo module version record
        @rtype: odoo.module.version
        """
        self.ensure_one()
        # candidate must have full_version_str to ensure both version and Odoo version have been input
        # this is to avoid error when calling this on the context of onchange where either of version or Odoo version have not been filled
        candidates = self.odoo_module_version_ids.filtered(lambda v: v.full_version_str)
        if candidates:
            try:
                # sort the record by full_version_str descending
                # Hint: list(map(int, [x if x.isdigit() else '0' for x in v.full_version_str.split('.')])) will
                # return a list like [12, 0, 6, 2, 1] presenting '12.0.6.2.1'. Any non-digit will be converted to 0.
                # For example, '12.0.6.2.beta' will become '12.0.6.2.0'
                return candidates.sorted(key=lambda v: list(map(int, [x if x.isdigit() else '0' for x in v.full_version_str.split('.')])), reverse=True)[0]
            except Exception as e:
                raise ValidationError(_("There is an error during latest version finding for the module %s. Here is the details:\n%s")
                                      % (self.display_name, str(e)))
        return self.env['odoo.module.version']

    @api.depends('odoo_module_version_ids', 'odoo_module_version_ids.full_version_str')
    def _compute_odoo_module_version_id(self):
        for r in self:
            r.odoo_module_version_id = r.get_latest_version() or False

    @api.depends('odoo_module_version_id', 'odoo_module_version_id.summary')
    def _compute_summary(self):
        for r in self:
            r.summary = r.odoo_module_version_id.summary if r.odoo_module_version_id else ''

    def _set_summary(self):
        for r in self:
            if r.summary and r.odoo_module_versions_count == 1:
                r.odoo_module_version_id.summary = r.summary

    @api.depends('odoo_module_version_id', 'odoo_module_version_id.description')
    def _compute_description(self):
        for r in self:
            r.description = r.odoo_module_version_id.description if r.odoo_module_version_id else ''

    def _get_desc(self):
        descriptions = self.mapped('odoo_module_version_id').read(['module_id', 'description_html'])
        mapped_data = dict([(it['module_id'][0], it['description_html']) for it in descriptions])
        for r in self:
            r.description_html = mapped_data.get(r.id, '')

    def _set_description(self):
        for r in self:
            if r.description and r.odoo_module_versions_count == 1:
                r.odoo_module_version_id.description = r.description

    @api.depends('odoo_module_version_id', 'odoo_module_version_id.name')
    def _compute_name(self):
        for r in self:
            r.name = r.odoo_module_version_id.name if r.odoo_module_version_id else ''

    def _set_name(self):
        for r in self:
            if r.odoo_module_version_id:
                r.odoo_module_version_id.name = r.name

    @api.depends('odoo_module_version_ids.odoo_version_id')
    def _compute_odoo_versions(self):
        for r in self:
            r.odoo_version_ids = r.odoo_module_version_ids.mapped('odoo_version_id')

    def _compute_odoo_module_versions_count(self):
        file_data = self.env['odoo.module.version'].read_group([('module_id', 'in', self.ids)], ['module_id'], ['module_id'])
        mapped_data = dict([(dict_data['module_id'][0], dict_data['module_id_count']) for dict_data in file_data])
        for r in self:
            r.odoo_module_versions_count = mapped_data.get(r.id, 0)

    def action_view_odoo_module_versions(self):
        odoo_module_versions = self.mapped('odoo_module_version_ids')
        action = self.env.ref('to_odoo_module.odoo_module_version_action')
        result = action.read()[0]

        # get rid off the default context
        result['context'] = {}

        if len(odoo_module_versions) != 1:
            result['domain'] = "[('module_id', 'in', %s)]" % str(self.ids)
        elif len(odoo_module_versions) == 1:
            res = self.env.ref('to_odoo_module.odoo_module_version_form_view', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = odoo_module_versions.id
        return result

    def _prepare_product_tmpl_attribute_lines_data(self):
        data = {}
        odoo_version_id = self._context.get('odoo_version_id', False)
        if odoo_version_id:
            # ensure we have odoo.version record instead of id in integer
            if isinstance(odoo_version_id, int):
                odoo_version_id = self.env['odoo.version'].browse(odoo_version_id)

            attr_val_ids = self.env['product.attribute.value'].search([('odoo_version_id', '=', odoo_version_id.id)])
            if attr_val_ids:
                data.update({
                    'attribute_id': self.env.ref('to_product_odoo_version.product_attribute_odoo_version').id,
                    # create link with the existing product attribute values
                    'value_ids': [(4, attr_val_id.id) for attr_val_id in attr_val_ids]
                    })
        return data

    def _prepare_product_template_data(self):
        self.ensure_one()
        software_categ_id = self.env.ref('to_odoo_module.product_category_odoo_apps')
        name = self._context.get('name', self.name)
        data = {
            'name': name,
            'default_code': self.technical_name,
            'type': 'service',
            'categ_id': software_categ_id.id,
            'uom_id': self.env.ref('uom.product_uom_unit').id,
            'list_price': 0.0,
            'odoo_module_id': self.id,
            }
        attribute_lines_data = self._prepare_product_tmpl_attribute_lines_data()
        if bool(attribute_lines_data):
            data['attribute_line_ids'] = [(0, 0, attribute_lines_data)]
        return data

    def _create_product_tmpl_if_not_exists(self):
        product_tmpl = self.find_product_tmpl()
        if not product_tmpl:
            product_tmpl = self.env['product.template'].create(self._prepare_product_template_data())
        return product_tmpl

    def _prepare_product_tmpl_update_data(self):
        update_data = {}
        product_tmpl_id = self.product_tmpl_id
        if product_tmpl_id:
            if self.name and product_tmpl_id.name != self.name:
                update_data['name'] = self.name
            if product_tmpl_id.default_code != self.technical_name:
                update_data['default_code'] = self.technical_name
            if self.image_1920:
                if not self._identical_images(product_tmpl_id.image_1920, self.image_1920):
                    update_data['image_1920'] = self.image_1920
            else:
                if not self._identical_images(product_tmpl_id.image_128, self.image_128):
                    update_data['image_128'] = self.image_128

            if product_tmpl_id.description_sale != self.summary:
                update_data['description_sale'] = self.summary
            if product_tmpl_id.description_purchase != self.summary:
                update_data['description_purchase'] = self.summary

        return update_data

    def _update_product_tmpl_data(self):
        """
        synchronize fields data from Module to Product Template
        """
        for r in self:
            update_data = r._prepare_product_tmpl_update_data()
            if bool(update_data):
                r.product_tmpl_id.write(update_data)

    @api.model_create_multi
    def create(self, vals_list):
        records = super(OdooModule, self).create(vals_list)
        for res in records:
            if not res.product_tmpl_id and self._context.get('generate_app_products', False):
                old_technical_name = self._context.get('old_technical_name', '')
                product_tmpl_id = res.with_context(
                    old_technical_name=old_technical_name,
                    name=res.name)._create_product_tmpl_if_not_exists()
                res.write({
                    'product_tmpl_id': product_tmpl_id.id
                })
        records._update_product_tmpl_data()
        return records

    def write(self, vals):
        res = super(OdooModule, self).write(vals)
        self._update_product_tmpl_data()
        return res

    def unlink(self):
        odoo_module_versions = self.mapped('odoo_module_version_ids')
        if odoo_module_versions:
            odoo_module_versions.unlink()
        return super(OdooModule, self).unlink()

    def action_view_download_stats(self):
        action = self.env.ref('to_odoo_module.odoo_module_version_download_stat_action')
        result = action.read()[0]
        result['view_mode'] = 'pivot,graph'
        res = self.env.ref('to_odoo_module.odoo_module_version_download_stat_pivot_view', False)
        result['views'] = [(res and res.id or False, 'pivot')]
        result['domain'] = "[('odoo_module_id', 'in', " + str(self.ids) + ")]"
        return result

    def action_rotate_token(self):
        odoo_module_versions = self.mapped('odoo_module_version_ids')
        odoo_module_versions.action_rotate_token()

    def find_product_tmpl(self):
        """
        Hooking method to filter later.
        Imagine you have 2 product templates, 1 subscription and 1 lifetime.
        These domain will get you the wrong product template, that means you will update that wrong product template to the wrong field,
        and then update it with wrong data.
        This method will be override in `viin_odoo_module_subscription` 
        """
        ProductTemplate = self.env['product.template'].with_context(active_test=False)
        ctx = self._context
        name = ctx.get('name', self.name)
        product_tmpl = ProductTemplate.search([
            ('default_code', '=', self.technical_name),
            ('name', '=', name),
            ('odoo_module_id.git_repository_id', '=', self.git_repository_id.id)])
        if not product_tmpl:
            product_tmpl = ProductTemplate.search([
                ('default_code', '=', self.technical_name),
                ('odoo_module_id.git_repository_id', '=', self.git_repository_id.id)])

        old_technical_name = ctx.get('old_technical_name', '')
        if not product_tmpl and old_technical_name:
            product_tmpl = ProductTemplate.search([
                ('odoo_module_id.git_repository_id', '=', self.git_repository_id.id),
                '|',
                    ('default_code', '=', old_technical_name),
                    ('odoo_module_version_ids.old_technical_name', '=', self.technical_name)])

        if not product_tmpl:
            product_tmpl = ProductTemplate.search([
                ('name', '=', name),
                ('odoo_module_id.git_repository_id', '=', self.git_repository_id.id)])
        return product_tmpl
