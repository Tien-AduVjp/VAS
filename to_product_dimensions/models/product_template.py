from odoo import fields, models, api


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    length = fields.Float(string='Length',
                             compute='_compute_length',
                             inverse='_inverse_length',
                             store=True,
                             help="The length of the product in millimeter")
    width = fields.Float(string='Width',
                            compute='_compute_width',
                            inverse='_inverse_width',
                            store=True,
                            help="The width of the product in millimeter")
    height = fields.Float(string='Height',
                             compute='_compute_height',
                             inverse='_inverse_height',
                             store=True,
                             help="The height of the product in millimeter")
    stowage_factor = fields.Float(string='SF',
                                     default=1.0,
                                     compute='_compute_stowage_factor',
                                     inverse='_inverse_stowage_factor',
                                     store=True,
                                     help='Stowage Factor, the factor that will be used in stowage volume calculation. I.e. Stowage Vol. = L * W * H * SF')
    stowage_volume = fields.Float(string='Stowage Volume',
                                     compute='_compute_stowage_volume',
                                     digits='Stock Volume',
                                     store=True, help="Stowage Volume of the product in cubic meters")

    concat_dimension_in_name = fields.Boolean(string='Dimensions in Name',
                                              default=False,
                                              help="Enable to concatenate dimensions in the product name")

    _sql_constraints = [
        ('check_possitive_length',
         'CHECK(length >= 0.0)',
         "The Length must be greater than or equal to 0."),

        ('width',
         'CHECK(width >= 0.0)',
         "The Width must be greater than or equal to 0."),

        ('check_possitive_height',
         'CHECK(height >= 0.0)',
         "The Height must be greater than or equal to 0."),
    ]

    def _inverse_length(self):
        for r in self:
            if len(r.product_variant_ids) == 1:
                r.product_variant_ids.length = r.length

    def _inverse_height(self):
        for r in self:
            if len(r.product_variant_ids) == 1:
                r.product_variant_ids.height = r.height


    def _inverse_width(self):
        for r in self:
            if len(r.product_variant_ids) == 1:
                r.product_variant_ids.width = r.width

    def _inverse_stowage_factor(self):
        for r in self:
            if len(r.product_variant_ids) == 1:
                r.product_variant_ids.stowage_factor = r.stowage_factor

    @api.depends('product_variant_ids', 'product_variant_ids.stowage_volume', 'length', 'width', 'height', 'stowage_factor', 'volume')
    def _compute_stowage_volume(self):
        unique_variants = self.filtered(lambda template: len(template.product_variant_ids) == 1)
        for template in unique_variants:
            template.stowage_volume = template.product_variant_ids.stowage_volume
        for template in (self - unique_variants):
            template.stowage_volume = 0.0

    @api.depends('product_variant_ids', 'product_variant_ids.length')
    def _compute_length(self):
        unique_variants = self.filtered(lambda template: len(template.product_variant_ids) == 1)
        for template in unique_variants:
            template.length = template.product_variant_ids.length
        for template in (self - unique_variants):
            template.length = 0.0

    @api.depends('product_variant_ids', 'product_variant_ids.height')
    def _compute_height(self):
        unique_variants = self.filtered(lambda template: len(template.product_variant_ids) == 1)
        for template in unique_variants:
            template.height = template.product_variant_ids.height
        for template in (self - unique_variants):
            template.height = 0.0

    @api.depends('product_variant_ids', 'product_variant_ids.stowage_factor')
    def _compute_stowage_factor(self):
        unique_variants = self.filtered(lambda template: len(template.product_variant_ids) == 1)
        for template in unique_variants:
            template.stowage_factor = template.product_variant_ids.stowage_factor
        for template in (self - unique_variants):
            template.stowage_factor = 0.0

    @api.depends('product_variant_ids', 'product_variant_ids.width')
    def _compute_width(self):
        unique_variants = self.filtered(lambda template: len(template.product_variant_ids) == 1)
        for template in unique_variants:
            template.width = template.product_variant_ids.width
        for template in (self - unique_variants):
            template.width = 0.0

    @api.onchange('length', 'width', 'height')
    def _onchange_dimensions(self):
        if self.length > 0 and self.width > 0 and self.height > 0:
            self.volume = self._calculate_vol(self.length, self.width, self.height)

    @api.model
    def create(self, vals):
        template = super(ProductTemplate, self).create(vals)
        # This is needed to set given values to first variant after creation
        related_vals = {}
        if vals.get('length', 0):
            related_vals['length'] = vals['length']
        if vals.get('width', 0):
            related_vals['width'] = vals['width']
        if vals.get('height', 0):
            related_vals['height'] = vals['height']
        if vals.get('stowage_factor', 0):
            related_vals['stowage_factor'] = vals['stowage_factor']
        if related_vals:
            template.write(related_vals)
        return template

    def _get_dimensions_for_name(self):
        return '[%s*%s*%s]' % (self.length, self.width, self.height)

    def name_get(self):
        # Prefetch the fields used by the `name_get`, so `browse` doesn't fetch other fields
        self.read(['name', 'default_code', 'concat_dimension_in_name'])
        res = super(ProductTemplate, self).name_get()
        res_dict = dict(res)
        products = self.browse(res_dict.keys())
        for product in products:
            if product.concat_dimension_in_name:
                res_dict[product.id] += ' %s' % product._get_dimensions_for_name()
        res = [(k, v) for k, v in res_dict.items()]
        return res

    @api.model
    def _calculate_vol(self, l, w, h, stowage_factor=1.0):
        """
        @param l: the length of the product in millimeters
        @type l: float
        @param w:  the width of the product in millimeters
        @type: w: float
        @param h: the height of the product in millimeters
        @type h: float
        @param stowage_factor: stowage factor
        @type stowage_factor: float
        @return: the volume of the product (in cubic meters) if the stowage_factor is 1, or the stowage volume otherwise
        @rtype: float
        """
        return l * w * h * stowage_factor / 1000000000
