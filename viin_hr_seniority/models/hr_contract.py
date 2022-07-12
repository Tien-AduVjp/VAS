# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.tools import relativedelta


class HrContract(models.Model):
    _inherit = 'hr.contract'

    years = fields.Float(string='Contract Age in years', compute='_compute_contract_age', search='_search_contract_age_in_years')
    months = fields.Float(string='Contract Age in months', compute='_compute_contract_age', search='_search_contract_age_in_months')
    contract_age_text = fields.Char(string='Contract Age', compute='_compute_contract_age')

    @api.depends('date_start', 'date_end')
    def _compute_contract_age(self):

        def relativedelta_to_text(diff):
            """
            Convert relativedelta object to text. For example
            relativedelta(years=+1, months=+11, days=+29) to say "1 year 11 months 29 days"
            """
            text = []
            if diff.years:
                if diff.years > 1:
                    text.append(_("%s years") % diff.years)
                else:
                    text.append(_("%s year") % diff.years)
            if diff.months:
                if diff.months > 1:
                    text.append(_("%s months") % diff.months)
                else:
                    text.append(_("%s month") % diff.months)
            if diff.days:
                if diff.days > 1:
                    text.append(_("%s days") % diff.days)
                else:
                    text.append(_("%s day") % diff.days)
            return " ".join(text) if text else False

        today = fields.Date.today()
        for r in self:
            years = 0
            text = False
            if r.date_start and r.date_start < today:
                end_date = r.date_end or today
                end_date = end_date if end_date <= today else today
                diff = relativedelta(end_date, r.date_start or today)
                years = self.env['to.base'].get_number_of_years_between_dates(r.date_start, end_date)
                text = relativedelta_to_text(diff)
            r.years = years
            r.months = years * 12
            r.contract_age_text = text

    def _filter_contract_age(self, operator, operand, by_field='years'):
        all_contracts = self.env['hr.contract'].search_read([], [by_field])
        if operator == '=':
            if operand:  # equal
                list_ids = [vals['id'] for vals in all_contracts if vals[by_field] == operand]
            else:  # is not set, equal = ""
                list_ids = [vals['id'] for vals in all_contracts if not vals[by_field]]
        elif operator == '!=':
            if operand:
                list_ids = [vals['id'] for vals in all_contracts if vals[by_field] != operand]
            else:  # is set
                list_ids = [vals['id'] for vals in all_contracts if vals[by_field]]
        elif operator == '>':
            list_ids = [vals['id'] for vals in all_contracts if vals[by_field] > operand]
        elif operator == '<':
            list_ids = [vals['id'] for vals in all_contracts if vals[by_field] < operand]
        elif operator == '>=':
            list_ids = [vals['id'] for vals in all_contracts if vals[by_field] >= operand]
        elif operator == '<=':
            list_ids = [vals['id'] for vals in all_contracts if vals[by_field] <= operand]
        else:
            return []
        return [('id', 'in', list_ids)]

    def _search_contract_age_in_years(self, operator, operand):
        return self._filter_contract_age(operator, operand, by_field='years')

    def _search_contract_age_in_months(self, operator, operand):
        return self._filter_contract_age(operator, operand, by_field='months')
