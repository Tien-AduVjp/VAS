from datetime import datetime, date
from dateutil.rrule import rrule, MONTHLY

from odoo import models, api, _
from odoo.exceptions import UserError
from odoo.tools import float_round


class UoM(models.Model):
    _inherit = 'uom.uom'

#     def write(self, vals):
#         if not self._context.get('ignore_subscription_category_check', False):
#             uom_categ_subscription = self.env.ref('to_uom_subscription.uom_categ_subscription')
#             change_factor = 'factor' in vals or 'factor_inv' in vals
#             change_category = 'category_id' in vals
#             change_uom_type = 'uom_type' in vals
#             if self.filtered(lambda uom: uom.category_id == uom_categ_subscription):
#                 if change_factor:
#                     raise UserError(_("You may not be able to modify the ratio of the unit of measures"
#                                       " that belong to the category %s")
#                                       % uom_categ_subscription.display_name)
#                 if change_category:
#                     raise UserError(_("You may not be able to modify the category of the unit of measures"
#                                       " that currently belong to the category %s")
#                                       % uom_categ_subscription.display_name)
#                 if change_uom_type:
#                     raise UserError(_("You may not be able to modify the type of the unit of measures"
#                                       " that currently belong to the category %s")
#                                       % uom_categ_subscription.display_name)
#         return super(UoM, self).write(vals)

    def _name_get(self):
        return "%s - %s" % (self.name, self.category_id.name) if self.category_id.concat_uom_name else self.name

    def name_get(self):
        result = []
        for r in self:
            result.append((r.id, r._name_get()))
        return result

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        domain = []
        if name:
            domain = ['|', ('category_id.name', '=ilike', name + '%'), ('name', operator, name)]
        uoms = self.search(domain + args, limit=limit)
        return uoms.name_get()

    @api.model
    def calculate_subscription_month_quantity(self, dt_start, dt_end, round=True, rounding_method='UP'):
        """
        This method calculates subscription months between two dates that should respect subscription month conversion ratio.
        For example,
        ============
            dt_start = datetime.datetime(2019,1,1), dt_end = datetime.datetime(2019,1,31) | result will be 1.0
            dt_start = datetime.datetime(2019,1,2), dt_end = datetime.datetime(2019,1,31) | result will be 1.0 (because Month=28 days as defined in the default data)
            dt_start = datetime.datetime(2019,1,3), dt_end = datetime.datetime(2019,3,31) | result will be 3.0 (because Month=28 days as defined in the default data)
            dt_start = datetime.datetime(2019,1,3), dt_end = datetime.datetime(2019,3,14) | result will be 2.5 (because Month=28 days as defined in the default data)

        :param dt_start: datetime.date | datetime.datetime
        :param dt_end: datetime.date | datetime.datetime
        :param round: round to subscription month uom's rounding factor
        :param rounding_method: which is either 'UP' or 'DOWN' or 'HALF-UP'

        :return: number of subscription months
        :rtype: float
        """

        def date2datetime(dt):
            return datetime.combine(dt, datetime.min.time()) if not isinstance(dt, datetime) else dt

        if dt_start == dt_end:
            return 0.0

        # convert the given dt_start and dt_end from datetime.date to datetime.datetime if they were datetime.date
        dt_start = date2datetime(dt_start)
        dt_end = date2datetime(dt_end)

        # build dates list that looks like [dt_start, first date of each month, dt_end]
        dates = [dt_start] # ensure we always have dt_start in the dates
        for dt in rrule(freq=MONTHLY, dtstart=dt_start, bymonthday=1, byhour=0, byminute=0, bysecond=0, until=dt_end):
            if dt not in dates:
                dates.append(dt)
        if dt_end not in dates:
            dates.append(dt_end)

        # start calculate months (in float) between the given dt_start and dt_end
        last_seen_dt = False
        months = 0.0
        uom_subscription_month = self.env.ref('to_uom_subscription.uom_subscription_month')
        uom_subscription_hour = self.env.ref('to_uom_subscription.uom_subscription_hour')
        for dt in dates:
            if not last_seen_dt:
                last_seen_dt = dt
                continue
            diff = dt - last_seen_dt
            if diff.days >= uom_subscription_month.factor_inv:
                months += 1.0
            else:
                hours = diff.total_seconds() / 3600
                months += uom_subscription_hour._compute_quantity(hours, uom_subscription_month, round=False)
            last_seen_dt = dt

        # if round, do float_round to the UOM's rounding factor. Otherwise, keep the result as is
        if round:
            months = float_round(months, precision_rounding=uom_subscription_month.rounding, rounding_method=rounding_method)
        return months
