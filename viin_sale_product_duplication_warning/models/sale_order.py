# -*- coding: utf-8 -*-

from odoo import models, api, fields, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    duplicated_product = fields.Boolean(string='Duplicated Product', compute='_compute_duplicated_product', search='_search_duplicated_product',
                                               help="Technical field that indicates if the order contains a product that appears more than 1 time.")
    product_duplication_warning = fields.Html(string='Product Duplication Warning', compute='_compute_product_duplication_warning',
                                              help="Technical field to store warning text for product duplication in the sales order.")

    def _compute_duplicated_product(self):
        order_ids = self._query_duplicated_product_order_ids()
        for r in self:
            r.duplicated_product = True if r.id in order_ids else False

    @api.model
    def _search_duplicated_product(self, operator, operand):
        if (operator == '=' and operand == True) or (operator == '!=' and operand == False):
            operator = 'in'
        else:
            operator = 'not in'
        return [('id', operator, self._query_duplicated_product_order_ids())]
    
    @api.depends('order_line', 'order_line.product_id')
    def _compute_product_duplication_warning(self):
        mapped_data = self._get_product_duplication_lines()
        for r in self:
            duplicated_lines = mapped_data.get(r, r.env['sale.order.line'])
            warn_list = []
            for product in duplicated_lines.with_context(active_test=False).product_id:
                lines = duplicated_lines.filtered(lambda l: l.with_context(active_test=False).product_id == product)
                warn_list.append(_("<li>The product <strong>%s</strong> was found appearing <strong>%s times</strong> at lines %s</li>")
                                 % (
                                     product.display_name,
                                     len(lines),
                                     _(" and ").join([str(line.sequence) for line in lines]))
                                 )
            if warn_list:
                r.product_duplication_warning = _("<strong>Product duplication found</strong><ul>%s</ul>") % ''.join(warn_list)
            else:
                r.product_duplication_warning = False
    
    def _get_product_duplication_lines(self):
        """
        Find order lines having product duplication in the same order

        :return dictionary of {order1: line_ids, order2: other_lines, ...}
        :rtype: dict
        """
        res = {}
        for r in self:
            res.setdefault(r, r.env['sale.order.line'])
            for product in r.order_line.with_context(active_test=False).filtered(lambda l: not l.product_id.ignore_product_duplication_warning).product_id:
                lines = r.order_line.filtered(lambda l: l.product_id == product)
                if len(lines) > 1:
                    res[r] |= lines
        return res

    @api.model
    def _query_duplicated_product_order_ids(self):
        # query for orders having the same product appearing for more than 1 time
        self.env.cr.execute("""
        SELECT sol.order_id AS order_id
        FROM sale_order_line AS sol
        JOIN product_product AS p ON p.id = sol.product_id
        JOIN product_template AS tmpl ON tmpl.id = p.product_tmpl_id
        WHERE tmpl.ignore_product_duplication_warning = false OR tmpl.ignore_product_duplication_warning IS NULL
        GROUP BY order_id, product_id
        HAVING count(*) > 1
        """)
        return [x[0] for x in set(self.env.cr.fetchall())]
