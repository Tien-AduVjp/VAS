from odoo import api, models


class StockMove(models.Model):
    _inherit = 'stock.move'

    @api.model_create_multi
    @api.returns('self', lambda value: value.id)
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('sale_line_id', False):
                sale_order = self.env['sale.order.line'].sudo().browse(vals['sale_line_id']).order_id
                company = sale_order.partner_id._find_company()
                if (
                    company
                    and company != sale_order.company_id
                    and company.applicable_on in ('sale', 'purchase', 'sale_purchase')
                ):
                    # the old flow:
                    # 1. Vendors -> Stock A (company A) -> Customers
                    # 2. Vendors -> Stock B (company B) -> Customers
                    # => an error occured because of the same serial on Customers location
                    # the new flow:
                    # 1. Vendors -> Stock A (company A) -> Inter Company Transit
                    vals['location_dest_id'] = self.env.ref('stock.stock_location_inter_wh').id
            elif vals.get('purchase_line_id', False):
                purchase_order = self.env['purchase.order.line'].sudo().browse(vals['purchase_line_id']).order_id
                company = purchase_order.partner_id._find_company()
                if (
                    company
                    and company != purchase_order.company_id
                    and company.applicable_on in ('sale', 'purchase', 'sale_purchase')
                ):
                    # the old flow:
                    # 2. Vendors -> Stock B (company B) -> Customers
                    # the new flow:
                    # 2. Inter Company Transit -> Stock B (company B) -> Customers
                    vals['location_id'] = self.env.ref('stock.stock_location_inter_wh').id
        return super(StockMove, self).create(vals_list)
