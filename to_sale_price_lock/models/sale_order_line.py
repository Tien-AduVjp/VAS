from odoo import models, api, _
from odoo.tools import float_compare
from odoo.exceptions import UserError


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    @api.constrains('price_unit', 'product_uom')
    def _check_price_unit_product_uom(self):
        for r in self:
            sale_price_access_group = r.order_id.company_id.sales_price_modifying_group_id
            prec = self.env['decimal.precision'].precision_get('Product Price')
            if r.company_id.lock_sales_prices and sale_price_access_group not in self.env.user.groups_id:
                if r.order_id.pricelist_id and r.order_id.partner_id:
                    product = r.product_id.with_context(
                        lang=r.order_id.partner_id.lang,
                        partner=r.order_id.partner_id,
                        quantity=r.product_uom_qty,
                        date=r.order_id.date_order,
                        pricelist=r.order_id.pricelist_id.id,
                        uom=r.product_uom.id,
                        fiscal_position=r.env.context.get('fiscal_position', False)
                    )
                    price_unit = self.env['account.tax']._fix_tax_included_price_company(r._get_display_price(product), product.taxes_id, r.tax_id, r.company_id)
                    if float_compare(r.price_unit, price_unit, precision_digits=prec) != 0:
                        raise UserError(_("You are not allowed to change the price of the product '%s'. Only users in "
                                          "the group of '%s' are allowed to do it")
                                          %(r.product_id.display_name, sale_price_access_group.display_name))
