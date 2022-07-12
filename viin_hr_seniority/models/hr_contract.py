from odoo import models, fields, api


class HrContract(models.Model):
    _inherit = 'hr.contract'

    years = fields.Float(string='Contract Age in years', compute='_compute_contract_age', search='_search_contract_age_in_years')
    months = fields.Float(string='Contract Age in months', compute='_compute_contract_age', search='_search_contract_age_in_months')

    def _compute_contract_age(self):
        today = fields.Date.today()
        for r in self:
            years = 0
            if r.date_start < today:
                end_date = r.date_end or today
                end_date = end_date if end_date <= today else today
                years = self.env['to.base'].get_number_of_years_between_dates(r.date_start, end_date)
            r.years = years
            r.months = years * 12

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
