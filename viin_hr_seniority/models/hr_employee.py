# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.tools import formatLang
from odoo.tools.date_utils import relativedelta


class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    
    first_contract_date = fields.Date(string='First Contract Date', compute='_compute_first_contract_date', store=True, tracking=True,
                                      groups='hr.group_hr_user',
                                      help="The boarding date of the employee, which is automatically computed using the"
                                      " start date of the first contract (including trial contracts) of this employee.")
    first_non_trial_contract_date = fields.Date(string='First Non-Trial Contract Date', compute='_compute_first_non_trial_contract_date',
                                                tracking=True, store=True, groups='hr.group_hr_user',
                                                help="The start date of the first non-trial contract of this employee.")
    termination_date = fields.Date(string='Termination Date', compute='_compute_termination_date', store=True,
                                   tracking=True, groups='hr.group_hr_user',
                                   help="The date on which the employee stop working for the company. It is computed"
                                   " using the end date of the last contract.")
    employee_seniority_ids = fields.One2many('hr.employee.seniority', 'employee_id', string='Seniority', readonly=True, groups='hr.group_hr_user')
    seniority_years = fields.Float(string='Seniority in years', compute='_compute_seniority', search='_seach_seniority_years',
                                   groups='hr.group_hr_user', compute_sudo=True,
                                   help="The employee's length of service in months which is calculated automatically"
                                   " by summarizing the related contracts periods")
    seniority_months = fields.Float(string='Seniority in months', compute='_compute_seniority', search='_seach_seniority_months',
                                    groups='hr.group_hr_user', compute_sudo=True,
                                    help="The employee's length of service in years which is calculated automatically"
                                    " by summarizing the related contracts periods")
    non_trial_seniority_years = fields.Float(string='Non-Trial Seniority in years', compute='_compute_non_trial_seniority',
                                             search='_seach_non_trial_seniority_years',
                                   groups='hr.group_hr_user', compute_sudo=True,
                                   help="The employee's length of service in months which is calculated automatically"
                                   " by summarizing the related non-trial contracts periods")
    non_trial_seniority_months = fields.Float(string='Non-Trial Seniority in months', compute='_compute_non_trial_seniority',
                                              search='_seach_non_trial_seniority_months',
                                    groups='hr.group_hr_user', compute_sudo=True,
                                    help="The employee's length of service in years which is calculated automatically"
                                    " by summarizing the related non-trial contracts periods")
    seniority_message = fields.Char(string='Seniority Message', compute='_compute_seniority_message', compute_sudo=True, groups='hr.group_hr_user')

    def _get_valid_contracts(self):
        contracts = self.contract_ids.filtered(lambda c: c.state in ['open', 'close'])
        if self._context.get('exclude_trial_contracts', False):
            contracts = contracts.filtered(lambda c: not c.trial_date_end or c.trial_date_end < c.date_start)
        return contracts

    @api.depends(
        'contract_ids',
        'contract_ids.date_start',
        'contract_ids.date_end',
        'contract_ids.trial_date_end',
        'contract_ids.state')
    def _compute_first_contract_date(self):
        self.flush()  # flush to update sql view for self.employee_seniority_ids
        seniority_records = self.employee_seniority_ids._filter_valid_employee_seniority().sorted('date_start')
        for r in self:
            emp_seniority_records = seniority_records.filtered(lambda c: c.employee_id == r)
            r.first_contract_date = emp_seniority_records[:1].date_start

    @api.depends(
        'contract_ids',
        'contract_ids.date_start',
        'contract_ids.date_end',
        'contract_ids.trial_date_end',
        'contract_ids.state')
    def _compute_first_non_trial_contract_date(self):
        self.flush()  # flush to update sql view for self.employee_seniority_ids
        seniority_records = self.employee_seniority_ids._filter_valid_employee_seniority().filtered(lambda rec: not rec.is_trial).sorted('date_start')
        for r in self:
            emp_seniority_records = seniority_records.filtered(lambda c: c.employee_id == r)
            r.first_non_trial_contract_date = emp_seniority_records[:1].date_start

    @api.depends(
        'contract_ids',
        'contract_ids.date_start',
        'contract_ids.date_end',
        'contract_ids.state')
    def _compute_termination_date(self):
        self.flush()  # flush to update sql view for self.employee_seniority_ids
        seniority_records = self.employee_seniority_ids._filter_valid_employee_seniority().sorted(
            lambda c: (c.date_start, c.date_end or fields.Date.today() + relativedelta(years=1000))
            )
        for r in self:
            emp_seniority_records = seniority_records.filtered(lambda c: c.employee_id == r)
            r.termination_date = emp_seniority_records[-1:].date_end or False

    def _compute_seniority(self):
        self.flush()  # flush to update sql view for self.employee_seniority_ids
        seniority_records = self.employee_seniority_ids._filter_valid_employee_seniority()
        for r in self:
            years = sum(seniority_records.filtered(lambda c: c.employee_id == r).mapped('service_years'))
            r.seniority_years = years
            r.seniority_months = years * 12

    def _compute_non_trial_seniority(self):
        self.flush()  # flush to update sql view for self.employee_seniority_ids
        seniority_records = self.employee_seniority_ids._filter_valid_employee_seniority().filtered(lambda rec: not rec.is_trial)
        for r in self:
            years = sum(seniority_records.filtered(lambda c: c.employee_id == r).mapped('service_years'))
            r.non_trial_seniority_years = years
            r.non_trial_seniority_months = years * 12
    
    def _compute_seniority_message(self):
        self.flush()  # flush to update sql view for self.employee_seniority_ids
        field_name_prefix = ''
        if self._context.get('exclude_trial_contracts', False):
            field_name_prefix = 'non_trial_'
        for r in self:
            years_mod = int(getattr(r, '%sseniority_years' % field_name_prefix) // 1)
            if years_mod == 1:
                year_term = _("year")
            elif years_mod > 1:
                year_term = _("years")
            else:
                year_term = ""
                
            terms = []
            if years_mod:
                terms.append(_("%s %s") % (years_mod, year_term))
            
            month_mod = getattr(r, '%sseniority_months' % field_name_prefix) % 12
            if month_mod == 1.0:
                month_term = _("month")
            else:
                month_term = _("months")

            if month_mod > 0.0:
                terms.append(_("%s %s") % (formatLang(self.env, month_mod, digits=2), month_term))
            if terms:
                r.seniority_message = ", ".join(terms)
            else:
                r.seniority_message = "0"
        
    def _filter_seniority_message(self, operator, operand, by_field='seniority_years'):
        all_employees = self.env['hr.employee'].search_read([], [by_field])
        if operator == '=':
            if operand:  # equal
                list_ids = [vals['id'] for vals in all_employees if vals[by_field] == operand]
            else:  # is not set, equal = ""
                list_ids = [vals['id'] for vals in all_employees if not vals[by_field]]
        elif operator == '!=':
            if operand:
                list_ids = [vals['id'] for vals in all_employees if vals[by_field] != operand]
            else:  # is set
                list_ids = [vals['id'] for vals in all_employees if vals[by_field]]
        elif operator == '>':
            list_ids = [vals['id'] for vals in all_employees if vals[by_field] > operand]
        elif operator == '<':
            list_ids = [vals['id'] for vals in all_employees if vals[by_field] < operand]
        elif operator == '>=':
            list_ids = [vals['id'] for vals in all_employees if vals[by_field] >= operand]
        elif operator == '<=':
            list_ids = [vals['id'] for vals in all_employees if vals[by_field] <= operand]
        else:
            return []
        return [('id', 'in', list_ids)]
                
    def _seach_seniority_years(self, operator, operand):
        return self._filter_seniority_message(operator, operand, by_field='seniority_years')
    
    def _seach_seniority_months(self, operator, operand):
        return self._filter_seniority_message(operator, operand, by_field='seniority_months')
    
    def _seach_non_trial_seniority_years(self, operator, operand):
        return self._filter_seniority_message(operator, operand, by_field='non_trial_seniority_years')
    
    def _seach_non_trial_seniority_months(self, operator, operand):
        return self._filter_seniority_message(operator, operand, by_field='non_trial_seniority_months')

    def action_view_employee_seniority(self):
        action = self.env.ref('viin_hr_seniority.action_hr_employee_seniority_report')
        result = action.read()[0]
        result.update({
            # override the context to get rid of the default filtering
            'context': {},
            'domain': "[('employee_id', 'in', %s)]" % self.ids
            })
        return result
            
