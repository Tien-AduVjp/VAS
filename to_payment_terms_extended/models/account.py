from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from dateutil.relativedelta import relativedelta


class AccountPaymentTermLine(models.Model):
    _inherit = 'account.payment.term.line'

    option = fields.Selection(selection_add=[
            ('fix_day_next_x_months', "Fixed day of Next X months"),
            ('last_day_next_x_months', 'Last day of Next X months'),
        ])
    fixed_day_of_month = fields.Integer(string="Day of month")
    number_of_next_month = fields.Integer(string="Number of next month")

    @api.constrains('fixed_day_of_month', 'number_of_next_month')
    def _check_fixed_day_and_number_of_month(self):
        for r in self.filtered(lambda t: t.option in ('fix_day_next_x_months', 'last_day_next_x_months')):
            if r.number_of_next_month < 0:
                raise ValidationError(_("The number of next month used for a payment term cannot be negative."))
            elif r.fixed_day_of_month < 0:
                raise ValidationError(_("The fixed day of month used for a payment term cannot be negative."))

    @api.onchange('option')
    def _onchange_option(self):
        if self.option == 'last_day_next_x_months':
            self.days = 0
            self.fixed_day_of_month = 0
        else:
            super(AccountPaymentTermLine, self)._onchange_option()


class AccountPaymentTerm(models.Model):
    _inherit = 'account.payment.term'

    def compute(self, value, date_ref=False, currency=None):
        result = super(AccountPaymentTerm, self).compute(value, date_ref=date_ref, currency=currency)

        date_ref = date_ref or fields.Date.today()
        amount = value
        sign = value < 0 and -1 or 1
        if not currency:
            currency_id = self.env.context.get('currency_id', False)
            if currency_id:
                currency = self.env['res.currency'].browse(currency_id)
            else:
                currency = self.env.company.currency_id
        index = 0
        for line in self.line_ids:
            if line.value == 'fixed':
                amt = sign * currency.round(line.value_amount)
            elif line.value == 'percent':
                amt = currency.round(value * (line.value_amount / 100.0))
            elif line.value == 'balance':
                amt = currency.round(amount)
            if amt:
                next_date = fields.Date.from_string(date_ref)
                if line.option == 'fix_day_next_x_months':
                    next_date += relativedelta(day=line.fixed_day_of_month, months=line.number_of_next_month)
                    result[index] = (fields.Date.to_string(next_date), amt)
                elif line.option == 'last_day_next_x_months':
                    next_date += relativedelta(day=31, months=line.number_of_next_month)
                    result[index] = (fields.Date.to_string(next_date), amt)
                index += 1
                amount -= amt
        return result
