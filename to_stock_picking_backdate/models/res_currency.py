from odoo import models


class ResCurrency(models.Model):
    _inherit = 'res.currency'
    
    def _convert(self, from_amount, to_currency, company, date, round=True):
        return super(ResCurrency, self)._convert(from_amount=from_amount,
                                                 to_currency=to_currency,
                                                 company=company,
                                                 date=self._context.get('manual_validate_date_time', False) or date,
                                                 round=round)
