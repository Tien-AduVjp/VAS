from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

MONTHS = [
    ('1', 'January'),
    ('2', 'February'),
    ('3', 'March'),
    ('4', 'April'),
    ('5', 'May'),
    ('6', 'June'),
    ('7', 'July'),
    ('8', 'August'),
    ('9', 'September'),
    ('10', 'October'),
    ('11', 'November'),
    ('12', 'December')
]

def compair_date_by_day_and_month(day1, month1, day2, month2):
    """
    Return:
        -1 if day1/month1 < day2/month2
        0 if day1/month1 == day2/month2
        1 if day1/month1 > day2/month2
    """
    if month1 < month2:
        return -1
    elif month1 == month2 and day1 < day2:
        return -1
    elif month1 == month2 and day1 == day2:
        return 0
    else:
        return 1


class ProductPricelistItem(models.Model):
    _inherit = 'product.pricelist.item'

    recurring = fields.Boolean('Recurring', default=False, help="Check this if you want to configure a recurring rule.")
    recurring_period = fields.Selection(selection=[('monthly', 'Monthly'), ('annually', 'Annually')], string='Recurring Period')
    recurring_day_from = fields.Integer('From Day', default=1)
    recurring_day_to = fields.Integer('To Day', default=1)
    recurring_month_from = fields.Selection(selection=MONTHS, string='From Month', default='1')
    recurring_month_to = fields.Selection(selection=MONTHS, string='To Month', default='1')

    @api.constrains('recurring', 'recurring_period',
                    'recurring_day_from', 'recurring_day_to',
                    'recurring_month_from', 'recurring_month_to')
    def _check_valid_recurring_day(self):
        for r in self.filtered(lambda item: item.recurring):
            if not (1 <= r.recurring_day_from <= 31 and 1 <= r.recurring_day_to <= 31):
                raise ValidationError(_("Days must be in range from 1 to 31."))
            if r.recurring_period == 'monthly':
                if r.recurring_day_from > r.recurring_day_to:
                    raise ValidationError(_("Day start cannot be greater than day end."))
            elif r.recurring_period == 'annually':
                if compair_date_by_day_and_month(r.recurring_day_from, int(r.recurring_month_from), r.recurring_day_to, int(r.recurring_month_to)) == 1:
                    raise ValidationError(_("Date start cannot be after date end."))


class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'

    def _compute_price_rule_get_items(self, products_qty_partner, date, uom_id, prod_tmpl_ids, prod_ids, categ_ids):
        records = super(ProductPricelist, self)._compute_price_rule_get_items(products_qty_partner, date, uom_id, prod_tmpl_ids, prod_ids, categ_ids)

        def filter_recurring_items(item):
            if not item.recurring:
                return True
            elif item.recurring_period == 'monthly':
                if item.recurring_day_from <= date.day <= item.recurring_day_to:
                    return True
            elif item.recurring_period == 'annually':
                if compair_date_by_day_and_month(item.recurring_day_from, int(item.recurring_month_from), date.day, date.month) < 1 \
                        and compair_date_by_day_and_month(item.recurring_day_to, int(item.recurring_month_to), date.day, date.month) > -1:
                    return True
            return False

        return records.filtered(filter_recurring_items)
