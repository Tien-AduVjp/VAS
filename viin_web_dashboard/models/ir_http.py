from odoo import models
from odoo.http import request


class IrHttp(models.AbstractModel):
    _inherit = 'ir.http'

    def session_info(self):
        res = super(IrHttp, self).session_info()
        if request.env.user.has_group('base.group_user'):
            # TODOS: get the current company in systemtray instead of the default company
            company_id = res['company_id']
            if company_id:
                currency = request.env['res.company'].browse(company_id).currency_id
            else:
                currency = request.env.user.company_ids[:1].currency_id
            res.update({
                'company_currency_id': currency.id,
                'decimal_places_of_currency': currency.decimal_places,
                })
        return res
