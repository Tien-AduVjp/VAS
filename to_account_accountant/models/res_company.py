from datetime import timedelta

from odoo import models
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, date_utils


class ResCompany(models.Model):
    _inherit = 'res.company'

    def compute_fiscalyear_dates(self, current_date):
        '''Override the one in the module `account` which return calendar year in order to
        computes the start and end dates of the fiscal year defined in the model `account.fiscal.year`
        where the given 'current_date' belongs to.

        :param current_date: A datetime.date/datetime.datetime object.
        :return: A dictionary containing:
            * date_from
            * date_to
            * [Optionally] record: The fiscal year record.
        '''
        self.ensure_one()
        date_str = current_date.strftime(DEFAULT_SERVER_DATE_FORMAT)

        # Search a fiscal year record containing the date.
        # If a record is found, then no need further computation, we get the dates range directly.
        fiscalyear = self.env['account.fiscal.year'].search([
            ('company_id', '=', self.id),
            ('date_from', '<=', date_str),
            ('date_to', '>=', date_str),
        ], limit=1)
        if fiscalyear:
            return {
                'date_from': fiscalyear.date_from,
                'date_to': fiscalyear.date_to,
                'record': fiscalyear,
            }

        date_from, date_to = date_utils.get_fiscal_year(
            current_date, day=self.fiscalyear_last_day, month=int(self.fiscalyear_last_month))

        date_from_str = date_from.strftime(DEFAULT_SERVER_DATE_FORMAT)
        date_to_str = date_to.strftime(DEFAULT_SERVER_DATE_FORMAT)

        # Search for fiscal year records reducing the delta between the date_from/date_to.
        # This case could happen if there is a gap between two fiscal year records.
        # E.g. two fiscal year records: 2017-01-01 -> 2017-02-01 and 2017-03-01 -> 2017-12-31.
        # => The period 2017-02-02 - 2017-02-30 is not covered by a fiscal year record.

        fiscalyear_from = self.env['account.fiscal.year'].search([
            ('company_id', '=', self.id),
            ('date_from', '<=', date_from_str),
            ('date_to', '>=', date_from_str),
        ], limit=1)
        if fiscalyear_from:
            date_from = fiscalyear_from.date_to + timedelta(days=1)

        fiscalyear_to = self.env['account.fiscal.year'].search([
            ('company_id', '=', self.id),
            ('date_from', '<=', date_to_str),
            ('date_to', '>=', date_to_str),
        ], limit=1)
        if fiscalyear_to:
            date_to = fiscalyear_to.date_from - timedelta(days=1)

        if not date_from or not date_to:
            super(ResCompany, self).compute_fiscalyear_dates()

        return {'date_from': date_from, 'date_to': date_to}
