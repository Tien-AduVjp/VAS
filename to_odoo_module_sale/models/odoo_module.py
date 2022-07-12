from odoo import models, fields, SUPERUSER_ID


class OdooModule(models.Model):
    _inherit = 'odoo.module'

    sales_count = fields.Float(string="Sales Count", compute="_compute_sales_count",
                                     help="The total sales count of all version of this module")

    def _compute_sales_count(self):
        odoo_module_versions = self.mapped('odoo_module_version_ids')
        if odoo_module_versions:
            odoo_module_versions = odoo_module_versions.with_user(SUPERUSER_ID)
            odoo_module_versions.read(['module_id', 'product_id'])
        for r in self.with_user(SUPERUSER_ID):
            r.sales_count = sum(odoo_module_versions.filtered(lambda omv: omv.module_id == r).mapped('product_id.sales_count'))

    def _get_combination_info(self, odoo_module_version=False, combination=False, add_qty=1, pricelist=False, parent_combination=False, only_template=False):
        odoo_module_version = odoo_module_version or self.odoo_module_version_id

        res = {
            'name': self.name,
            'external_downloads_count': self.external_downloads_count,
            'sales_count': self.sales_count,
            'already_purchase': False,
            }
        partner = self._context.get('partner', False)
        pricelist_id = pricelist or self._context.get('pricelist', False)
        pricelist = self.env['product.pricelist'].browse(pricelist_id)

        if partner:
            recursive_dependencies = odoo_module_version.with_context(partner=partner).get_unbought_recursive_dependencies(incl_the_current=True)
            if not recursive_dependencies:
                res['already_purchase'] = True
        else:
            recursive_dependencies = odoo_module_version.with_context(exclude_standard_odoo_modules=True).get_recursive_dependencies(incl_the_current=True)
        res['lst_price'] = sum(recursive_dependencies.mapped('product_id.lst_price'))
        list_price, price, has_discounted_price = [], [], []
        for dependency in recursive_dependencies:
            # We should not give current module version product_id.id to this loop, it cause tremendous hazard result.
            # This is dependency product info. When we give this module product_id to `_get_combination_info()`,
            # it just give us the current product price instead of giving us the dependency product price.
            odoo_module_version_info = dependency.product_tmpl_id._get_combination_info(
                    combination=combination,
                    product_id=dependency.product_id.id,
                    add_qty=add_qty,
                    pricelist=pricelist,
                    parent_combination=parent_combination,
                    only_template=only_template
                )
            list_price.append(odoo_module_version_info['list_price'])
            price.append(odoo_module_version_info['price'])
            has_discounted_price.append(odoo_module_version_info['has_discounted_price'])
        res.update({
            'list_price': sum(list_price),
            'price': sum(price),
            'has_discounted_price': any(has_discounted_price)
            })
        return res
