from odoo import models, fields, api


class ProductPricelistItem(models.Model):
    _inherit = 'product.pricelist.item'

    sequence = fields.Integer(string='Sequence', required=True, default=1)
    days_of_week = fields.Boolean(string='Days Of Week', default=False, help="If this field marked, show days of week")
    mon = fields.Boolean(string='Monday', default=False)
    tue = fields.Boolean(string='Tuesday', default=False)
    wed = fields.Boolean(string='Wednesday', default=False)
    thu = fields.Boolean(string='Thursday', default=False)
    fri = fields.Boolean(string='Friday', default=False)
    sat = fields.Boolean(string='Saturday', default=False)
    sun = fields.Boolean(string='Sunday', default=False)

    @api.onchange('days_of_week')
    def _onchange_days_of_week(self):
        if self.days_of_week == False:
            self.mon = False
            self.tue = False
            self.wed = False
            self.thu = False
            self.fri = False
            self.sat = False
            self.sun = False


class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'

    def _compute_price_rule_get_items(self, products_qty_partner, date, uom_id, prod_tmpl_ids, prod_ids, categ_ids):
        res = super(ProductPricelist, self)._compute_price_rule_get_items(products_qty_partner, date, uom_id, prod_tmpl_ids, prod_ids, categ_ids)
        dow = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
        weekday = date.weekday()
        records = res.filtered(lambda item: not item.days_of_week or getattr(item, dow[weekday], False)).sorted('sequence')
        return records
