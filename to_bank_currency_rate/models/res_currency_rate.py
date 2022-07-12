from odoo import api, fields, models


class ResCurrencyRate(models.Model):
    _inherit = "res.currency.rate"

    exchange_type = fields.Selection([('buy_rate', 'Buy Rate'), ('transfer_rate', 'Transfer Rate'), ('sell_rate', 'Sell Rate')], string='Exchange Type',
                                     help="Buy Rate: the rate applied when we buy;\n"
                                     "Transfer Rate: the rate applied in custom declaration.\n"
                                     "Sell Rate: the rate applied when we sell.\n"
                                     "Leave it empty if the rate is not specific to Buy/Sell activities")
    bank_id = fields.Many2one('res.bank', string='Bank', help="The bank that the rate is applied")

    _sql_constraints = [
        ('unique_name_per_day',
         'unique (name,currency_id,company_id,bank_id,exchange_type)',
         'Only one currency rate per day per bank per Exchange Type allowed!'),
    ]
    
    @api.constrains('name', 'currency_id', 'company_id', 'bank_id')
    def _constraint_currency_rate_unique_name_per_day(self):
        self = self.filtered(lambda line: not line.bank_id)
        return super(ResCurrencyRate, self)._constraint_currency_rate_unique_name_per_day()
