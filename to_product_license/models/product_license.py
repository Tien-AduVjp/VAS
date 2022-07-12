from odoo import models, fields, api


class ProductLicense(models.Model):
    _name = 'product.license'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Product License'

    name = fields.Char(string='License Name', required=True, translate=True, tracking=True)
    active = fields.Boolean('Active', default=True, help="If unchecked, it will allow you to hide the license without removing it.")
    short_name = fields.Char(string='Short Name', required=True)

    product_license_version_ids = fields.One2many('product.license.version', 'license_id', string='Versions')
    versions_count = fields.Integer(string='Versions Count', compute='_compute_versions_count')

    first_version_id = fields.Many2one('product.license.version', compute='_compute_releases')
    first_released_date = fields.Date(string='First Released', compute='_compute_releases')

    latest_version_id = fields.Many2one('product.license.version', compute='_compute_releases')
    latest_released_date = fields.Date(string='Latest Released', compute='_compute_releases')
    summary = fields.Text(string='Summary', translate=True, tracking=True)
    ref_url = fields.Char(string='Ref. URL', tracking=True)
    product_ids = fields.Many2many('product.product', 'product_product_product_license_rel', 'product_license_id', 'product_id', string='Products', readonly=True)
    products_count = fields.Integer(string='Products Count', compute='_compute_products_count', store=True)

    def _compute_versions_count(self):
        versions_data = self.env['product.license.version'].with_context(active_test=False).read_group([('license_id', 'in', self.ids)], ['license_id'], ['license_id'])
        mapped_data = dict([(version_dict['license_id'][0], version_dict['license_id_count']) for version_dict in versions_data])
        for r in self:
            r.versions_count = mapped_data.get(r.id, 0)

    @api.depends('product_license_version_ids', 'product_license_version_ids.date_released')
    def _compute_releases(self):
        for r in self:
            first_version_id = False
            first_released_date = False
            latest_version_id = False
            latest_released_date = False

            if r.product_license_version_ids:
                product_license_versions = r.product_license_version_ids.sorted('date_released')
                first_version_id = product_license_versions[0].id
                first_released_date = product_license_versions[0].date_released
                latest_version_id = product_license_versions[-1].id
                latest_released_date = product_license_versions[-1].date_released

            r.update({
                'first_version_id': first_version_id,
                'first_released_date': first_released_date,
                'latest_version_id': latest_version_id,
                'latest_released_date': latest_released_date
                })

    @api.depends('product_ids')
    def _compute_products_count(self):
        for r in self:
            r.products_count = len(r.product_ids)

    @api.onchange('name')
    def _onchange_name(self):
        if self.name:
            short_name = ""
            for word in self.name.split():
                short_name += word[0]
            self.short_name = short_name

    def toggle_active(self):
        super(ProductLicense, self).toggle_active()
        for r in self:
            r.with_context(active_test=False).product_license_version_ids.filtered(lambda v: v.active != r.active).toggle_active()

    def action_view_products(self):
        product_ids = self.mapped('product_ids')

        action = self.env['ir.actions.act_window']._for_xml_id('product.product_normal_action')

        # choose the view_mode accordingly
        products_count = len(product_ids)
        if products_count != 1:
            action['domain'] = "[('id', 'in', " + str(product_ids.ids) + ")]"
        elif products_count == 1:
            res = self.env.ref('product.product_normal_form_view', False)
            action['views'] = [(res and res.id or False, 'form')]
            action['res_id'] = product_ids.id
        return action

    def action_view_versions(self):
        self.ensure_one()

        license_version_ids = self.with_context(active_test=False).mapped('product_license_version_ids')

        action = self.env['ir.actions.act_window']._for_xml_id('to_product_license.product_license_version_action')
        action['context'] = {'default_license_id': self.id}

        # choose the view_mode accordingly
        license_versions_count = len(license_version_ids)
        if license_versions_count != 1:
            action['domain'] = "[('license_id', 'in', " + str(self.ids) + "),'|',('active','=',True),('active','=',False)]"
        elif license_versions_count == 1:
            res = self.env.ref('to_product_license.product_license_version_view_form', False)
            action['views'] = [(res and res.id or False, 'form')]
            action['res_id'] = license_version_ids.id
        return action
