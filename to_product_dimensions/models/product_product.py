import threading

from odoo import fields, models, api


class ProductProduct(models.Model):
    _inherit = 'product.product'

    length = fields.Float(string="Length",
                             index=True,
                             help="The length of the product in millimeter")
    width = fields.Float(string="Width",
                            index=True,
                            help="The width of the product in millimeter")
    height = fields.Float(string="Height",
                             index=True,
                             help="The height of the product in millimeter")
    stowage_factor = fields.Float(string="SF",
                                     default=1,
                                     index=True,
                                     help='Stowage Factor, the factor that will be used in stowage volume calculation. I.e. Stowage Vol. = L * W * H * SF')
    stowage_volume = fields.Float(string="Stowage Volume",
                                     index=True,
                                     compute='_compute_stowage_volume',
                                     digits='Stock Volume',
                                     store=True, help="The stowage volume of the product in cubic meters")

    volume = fields.Float(compute='_compute_volume', inverse='_set_volume', store=True)

    _sql_constraints = [
        ('check_possitive_length',
         'CHECK(length >= 0.0)',
         "The Length must be greater than 0."),

        ('width',
         'CHECK(width >= 0.0)',
         "The Width must be greater than 0."),

        ('check_possitive_height',
         'CHECK(height >= 0.0)',
         "The Height must be greater than 0."),
    ]

    def _get_dimensions_for_name(self):
        return '[%s*%s*%s]' % (self.length, self.width, self.height)

    def name_get(self):
        res = super(ProductProduct, self).name_get()
        # skip manually method in test mode to avoid error when running unit test of Odoo
        if getattr(threading.currentThread(), 'testing', False) or self.env.registry.in_test_mode():
            return res
        res_dict = dict(res)
        product_ids = self.browse(res_dict.keys())
        for product_id in product_ids:
            if product_id.concat_dimension_in_name:
                res_dict[product_id.id] += ' %s' % product_id._get_dimensions_for_name()
        res = [(k, v) for k, v in res_dict.items()]
        return res

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
        return self.product_tmpl_id._calculate_vol(l=l, w=w, h=h, stowage_factor=stowage_factor)

    @api.depends('length', 'width', 'height')
    def _compute_volume(self):
        for r in self:
            r.volume = r._calculate_vol(r.length, r.width, r.height)

    def _set_volume(self):
        pass

    @api.depends('volume', 'stowage_factor')
    def _compute_stowage_volume(self):
        for r in self:
            r.stowage_volume = r.volume * r.stowage_factor

