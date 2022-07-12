from odoo import models, fields


class OdooModuleVersion(models.Model):
    _inherit = 'odoo.module.version'

    sales_count = fields.Float(related='product_id.sales_count', string='# Sales')
    
    def _get_combination_info_variant(self, add_qty=1, pricelist=False, parent_combination=False):
        """
        This function was create because application products was built modularized, a product
        depends to several another application product, which make product price is sum of itself
        and all of its dependencies.
        :param: add_qty: float with the quantity for which to get the info, indeed some pricelist
            rules might depend on it.
        :param: pricelist: `product.pricelist` record, the pricelist to use (can be none,
            eg. from SO if no partner and no pricelist selected)
        :param: parent_combination: if no combination and no product_id are given, it will
            try to find the first possible combination, taking into account parent_combination
            (if set) for the exclusion rules.
        :context: partner: `res.partner` record, the partner who bought this SO.
        :context: product: `product.product` record, the product variant for which this module
            version presents for accounting integration, default is product_id of module version.
        :retype: dict
        :return: dict data include these content:
            - name: name of product (odoo module version)
            - external_downloads_count: number of external users download times for all
                versions of this module.
            - sales_count: number of sales for all versions of this module.
            - already_purchase: which is this partner purchased module version or not (
                include all of its dependencies).
            - lst_price: the sale price is managed from the product template, click on
                the 'Configure Variants' button to set the extra attribute prices.
            - list_price:the catalog price of the combination  (include dependencies),
                but this is not the "real" list_price, it has price_extra included (so
                it's actually more closely related to `lst_price`), and it is converted
                to the pricelist currency (if given).
            - price: the computed price of the combination (include dependencies), take
                the catalog price if no pricelist is given.
            - has_discounted_price: True if any of product (include dependency product),
                has discounted price, else False.
        """
        self.ensure_one()
        res = {
            'name': self.name,
            'external_downloads_count': self.module_id.external_downloads_count,
            'sales_count': self.module_id.sales_count,
            'already_purchase': False,
            }
        partner = self._context.get('partner', False)
        product = self._context.get('product', self.product_id)
        pricelist_id = pricelist or self._context.get('pricelist', False)
        pricelist = self.env['product.pricelist'].browse(pricelist_id)
        recursive_dependencies = product.with_context(partner=partner).get_app_product_dependencies(incl_the_current=True)
        if not recursive_dependencies:
            res['already_purchase'] = True
        res['lst_price'] = sum(recursive_dependencies.mapped('lst_price'))
        list_price, price, has_discounted_price = [], [], []
        for dependency in recursive_dependencies:
            odoo_module_version_info = dependency._get_combination_info_variant(add_qty, pricelist, parent_combination)
            list_price.append(odoo_module_version_info['list_price'])
            price.append(odoo_module_version_info['price'])
            has_discounted_price.append(odoo_module_version_info['has_discounted_price'])
        res.update({
            'list_price': sum(list_price),
            'price': sum(price),
            'has_discounted_price': any(has_discounted_price)
            })
        return res
