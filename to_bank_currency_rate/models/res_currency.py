import inspect

from psycopg2.extensions import AsIs
from odoo import models, api


class ResCurrency(models.Model):
    _inherit = "res.currency"

    def _get_bank_currency_ex_rate_supported_models(self):
        return {
            'account.move': '_get_currency_context',
            'account.move.line': '_get_currency_context',
            'account.payment': '_get_currency_context',
            'account.bank.statement.line': '_get_currency_context',
            }

    def _get_rates(self, company, date):

        def _get_caller_records():
            stact = inspect.stack()
            for i, stack in enumerate(stact):
                if stack.function == '_convert' and stact[i+1].function != '_convert':
                    return stact[i+1].frame.f_locals.get('self', False)
                if stack.function == '_compute_current_rate' and stact[i+1].function != '_compute_current_rate':
                    return stact[i+4].frame.f_locals.get('self', False)
            return False

        self.env['res.currency.rate'].flush([
            'rate',
            'currency_id',
            'company_id',
            'name',
            'exchange_type',
            'bank_id',
            ])

        exchange_rate_bank = self._context.get('exchange_rate_bank', company.main_currency_bank_id)
        exchange_type = self._context.get('exchange_type', False)

        caller_records = _get_caller_records()
        supported_models = self._get_bank_currency_ex_rate_supported_models()
        if (not exchange_rate_bank or not exchange_type) \
            and hasattr(caller_records, '_name') and caller_records._name in supported_models.keys() \
            and len(caller_records) == 1:
            exchange_rate_bank, exchange_type = getattr(caller_records, supported_models[caller_records._name])()

        exchange_rate_bank_condition = exchange_rate_sub_bank_condition = exchange_type_condition = ""
        if exchange_rate_bank:
            exchange_rate_bank_condition = "AND r.bank_id = {}".format(int(exchange_rate_bank.id))
            if exchange_rate_bank != company.main_currency_bank_id:
                exchange_rate_sub_bank_condition = "AND r.bank_id = {}".format(int(company.main_currency_bank_id.id))
            if exchange_type:
                exchange_type_condition = "AND r.exchange_type='{}'".format(exchange_type)


        query = """SELECT c.id,
                  COALESCE(
                      (SELECT r.rate FROM res_currency_rate r
                      WHERE r.currency_id = c.id AND r.name <= %s
                          AND (r.company_id IS NULL OR r.company_id = %s)
                          %s
                          %s
                      ORDER BY r.company_id, r.name DESC, r.write_date DESC
                      LIMIT 1),
                      COALESCE(
                          (SELECT r.rate FROM res_currency_rate r
                          WHERE r.currency_id = c.id AND r.name <= %s
                              AND (r.company_id IS NULL OR r.company_id = %s)
                              %s
                              %s
                          ORDER BY r.company_id, r.name DESC, r.write_date DESC
                          LIMIT 1),
                          COALESCE((SELECT r.rate FROM res_currency_rate r
                              WHERE r.currency_id = c.id AND r.name <= %s
                                AND (r.company_id IS NULL OR r.company_id = %s)
                           ORDER BY r.company_id, r.name DESC, r.write_date DESC
                              LIMIT 1), 1.0))) AS rate
           FROM res_currency c
           WHERE c.id IN %s"""
        self._cr.execute(query, (date, company.id, AsIs(exchange_type_condition), AsIs(exchange_rate_bank_condition),
                                 date, company.id, AsIs(exchange_type_condition), AsIs(exchange_rate_sub_bank_condition),
                                 date, company.id, tuple(self.ids)))
        currency_rates = dict(self._cr.fetchall())
        return currency_rates

    @api.depends('rate_ids.rate', 'rate_ids.bank_id', 'rate_ids.exchange_type')
    def _compute_current_rate(self):
        return super(ResCurrency, self)._compute_current_rate()
