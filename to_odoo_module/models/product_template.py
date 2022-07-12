from odoo import models, fields, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    odoo_module_id = fields.Many2one('odoo.module', string='Related Odoo Module', readonly=True)
    is_odoo_app = fields.Boolean(string='Is Odoo App', compute='_compute_odoo_module', store=True,
                                 help="This field is to indicate if this product represents Odoo Apps")

    odoo_modules_count = fields.Integer(string='Odoo Modules Count', compute='_compute_odoo_modules_count')

    odoo_module_version_ids = fields.One2many('odoo.module.version', 'product_tmpl_id', string='Odoo Module Versions')
    odoo_module_versions_count = fields.Integer(string='Odoo Module Versions Count', compute='_compute_odoo_module_versions_count')

    odoo_module_version_image_ids = fields.One2many('odoo.module.version.image', 'product_tmpl_id', string='Odoo Module Images', readonly=True)

    @api.depends('odoo_module_id')
    def _compute_odoo_module(self):
        for r in self:
            r.is_odoo_app = True if r.odoo_module_id else False

    def _compute_odoo_modules_count(self):
        odoo_module_data = self.env['odoo.module'].read_group([('product_tmpl_id', 'in', self.ids)], ['product_tmpl_id'], ['product_tmpl_id'])
        mapped_data = dict([(dict_data['product_tmpl_id'][0], dict_data['product_tmpl_id_count']) for dict_data in odoo_module_data])
        for r in self:
            r.odoo_modules_count = mapped_data.get(r.id, 0)

    def _compute_odoo_module_versions_count(self):
        file_data = self.env['odoo.module.version'].read_group([('product_tmpl_id', 'in', self.ids)], ['product_tmpl_id'], ['product_tmpl_id'])
        mapped_data = dict([(dict_data['product_tmpl_id'][0], dict_data['product_tmpl_id_count']) for dict_data in file_data])
        for r in self:
            r.odoo_module_versions_count = mapped_data.get(r.id, 0)

    def action_view_odoo_modules(self):
        # TODO: remove because one product template has only a odoo module
        odoo_modules = self.mapped('odoo_module_id')
        action = self.env.ref('to_odoo_module.odoo_module_action')
        result = action.read()[0]

        # choose the view_mode accordingly
        modules_count = len(odoo_modules)
        if modules_count != 1:
            result['domain'] = "[('product_tmpl_id', 'in', " + str(self.ids) + ")]"
        elif modules_count == 1:
            res = self.env.ref('to_odoo_module.odoo_module_form_view', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = odoo_modules.id
        return result

    def action_view_odoo_module_versions(self):
        odoo_module_versions = self.mapped('odoo_module_version_ids')
        action = self.env.ref('to_odoo_module.odoo_module_version_action')
        result = action.read()[0]

        # get rid off the default context
        result['context'] = {}

        # choose the view_mode accordingly
        modules_count = len(odoo_module_versions)
        if modules_count != 1:
            result['domain'] = "[('product_tmpl_id', 'in', " + str(self.ids) + ")]"
        elif modules_count == 1:
            res = self.env.ref('to_odoo_module.odoo_module_version_form_view', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = odoo_module_versions.id
        return result

    @api.depends('odoo_module_id')
    def _compute_default_code(self):
        super(ProductTemplate, self)._compute_default_code()
        for template in self.filtered(lambda pt: pt.odoo_module_id):
            template.default_code = template.odoo_module_id.odoo_module_version_id.technical_name
