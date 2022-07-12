from odoo import models, fields, api


class ProductCollection(models.Model):
    _name = 'product.collection'
    _inherit = 'mail.thread'
    _description = 'Product Collection'

    name = fields.Char(string='Title', required=True, translate=True, index=True, tracking=True,)
    active = fields.Boolean(string='Active', default=True, help="If unchecked, it will allow you to hide"
                            " the collection without removing it.")
    description = fields.Text(string='Description', translate=True)
    product_tmpl_ids = fields.One2many('product.template', 'collection_id', string='Product Templates')
    product_tmpls_count = fields.Integer(string='Product Templates Count', compute='_compute_product_tmpls_count')
    product_ids = fields.One2many('product.product', 'collection_id', string='Products')
    products_count = fields.Integer(string='Products Count', compute='_compute_products_count')

    _sql_constraints = [
        ('name_description_check',
         'CHECK(name != description)',
         "The title of the collection should not be the description"),

        ('name_unique',
         'UNIQUE(name)',
         "The collection title must be unique"),
    ]

    @api.depends('product_tmpl_ids')
    def _compute_product_tmpls_count(self):
        total_data = self.env['product.template'].read_group([('collection_id', 'in', self.ids)], ['collection_id'], ['collection_id'])
        mapped_data = dict([(dict_data['collection_id'][0], dict_data['collection_id_count']) for dict_data in total_data])
        for r in self:
            r.product_tmpls_count = mapped_data.get(r.id, 0)

    @api.depends('product_ids')
    def _compute_products_count(self):
        total_data = self.env['product.product'].read_group([('collection_id', 'in', self.ids)], ['collection_id'], ['collection_id'])
        mapped_data = dict([(dict_data['collection_id'][0], dict_data['collection_id_count']) for dict_data in total_data])
        for r in self:
            r.products_count = mapped_data.get(r.id, 0)

    def action_view_product_templates(self):
        prod_tmpl_ids = self.product_tmpl_ids

        result = self.env['ir.actions.actions']._for_xml_id('product.product_template_action')

        # override the context to get rid of the default filtering
        result['context'] = {}

        prod_tmpls_count = len(prod_tmpl_ids)
        # choose the view_mode accordingly
        if prod_tmpls_count != 1:
            result['domain'] = "[('collection_id', 'in', %s)]" % self.ids
        elif prod_tmpls_count == 1:
            res = self.env.ref('product.product_template_only_form_view', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = prod_tmpl_ids.id
        return result

    def action_view_products(self):
        product_ids = self.product_ids

        result = self.env['ir.actions.actions']._for_xml_id('product.product_normal_action_sell')

        # override the context to get rid of the default filtering
        result['context'] = {}

        prod_count = len(product_ids)
        # choose the view_mode accordingly
        if prod_count != 1:
            result['domain'] = "[('collection_id', 'in', %s)]" % self.ids
        elif prod_count == 1:
            res = self.env.ref('product.product_normal_form_view', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = product_ids.id
        return result

