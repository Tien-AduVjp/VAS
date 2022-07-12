from odoo import models, fields


class ProductPublicCategory(models.Model):
    _inherit = 'product.public.category'

    odoo_module_version_ids = fields.Many2many('odoo.module.version', 'odoo_module_version_prod_public_categ_rel', 'public_categ_id', 'odoo_module_version_id',
                                        string='Odoo Module Versions')

    def get_most_download_odoo_modules(self, search=None, price=None, version=None, limit=4, offset=0):
        return self.env['odoo.module.version'].get_most_downloaded(search=search, category=self, price=price, version=version, limit=limit, offset=offset)

    def get_new_odoo_modules(self, search=None, price=None, version=None, limit=4, offset=0):
        return self.env['odoo.module.version'].get_new(search=search, category=self, price=price, version=version, limit=limit, offset=offset)

    def get_top_odoo_modules(self, search=None, price=None, version=None, limit=4, offset=0):
        return self.env['odoo.module.version'].get_top_rated(search=search, category=self, price=price, version=version, limit=limit, offset=offset)

    def get_best_sold_odoo_modules(self, search=None, price=None, version=None, limit=4, offset=0):
        return self.env['odoo.module.version'].get_best_sold_odoo_modules(search=search, category=self, price=price, version=version, limit=limit, offset=offset)

    def get_odoo_module_top_charts(self, limit=4, offset=0):
        return {
            'top_ids': self.get_top_rated(limit=limit, offset=offset),
            'new_ids': self.get_new(limit=limit, offset=offset),
            'most_download_ids': self.get_most_downloaded(limit=limit, offset=offset),
            'top_charts': 1
            }