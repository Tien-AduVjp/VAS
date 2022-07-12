from odoo import models, fields, api


class Picking(models.Model):
    _inherit = 'stock.move'

    def _get_price_unit_currency_conversion(self):
        """
            Get the price unit in corresponding currency in order to print the stock picking.
            The price unit on each stock move generated from a Purchase Order is already converted.
            We only need to convert the price unit generated from a Sale Order.
        """
        for r in self:
            price_unit = abs(r.price_unit)
            if r.sale_line_id:
                price_unit = r.sale_line_id.currency_id._convert(
                    from_amount=abs(r.sale_line_id.price_unit),
                    to_currency=r.picking_id.currency_id,
                    date=fields.Date.to_date(r.picking_id.sale_id.date_order),
                    company=r.company_id,
                )
            return price_unit
