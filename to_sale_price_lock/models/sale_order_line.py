from odoo import models, fields, api, _
from odoo.tools import float_compare


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    def _can_change_price_unit(self):
        sale_price_access_group = self.env.company.sales_price_modifying_group_id
        self._cr.execute("""SELECT 1 FROM res_groups_users_rel WHERE uid=%s AND gid =%s""",
                         (self._uid, sale_price_access_group.id))
        return bool(self._cr.fetchone())

    @api.onchange('price_unit', 'product_uom')
    def _onchange_price_unit_product_uom(self):
        res = {}
        sale_price_access_group = self.env.company.sales_price_modifying_group_id
        if not self.product_uom or not self.product_id:
            self.price_unit = 0.0
            return res

        if not self._can_change_price_unit():
            prec = self.env['decimal.precision'].precision_get('Product Price')
            if self.order_id.pricelist_id and self.order_id.partner_id:
                product = self.product_id.with_context(
                    lang=self.order_id.partner_id.lang,
                    partner=self.order_id.partner_id,
                    quantity=self.product_uom_qty,
                    date=self.order_id.date_order,
                    pricelist=self.order_id.pricelist_id.id,
                    uom=self.product_uom.id,
                    fiscal_position=self.env.context.get('fiscal_position')
                )
                price_unit = self.env['account.tax']._fix_tax_included_price_company(self._get_display_price(product), product.taxes_id, self.tax_id, self.company_id)
                if float_compare(self.price_unit, price_unit, precision_digits=prec) != 0:
                    self.price_unit = price_unit
                    res['warning'] = {
                        'title':_('Warning!'),
                        'message': _("You are not allowed to change the price of the product. Only users in "
                                     "the group of '%s' are allowed to do it")
                                      % (sale_price_access_group.display_name,)
                                    }
        return res
