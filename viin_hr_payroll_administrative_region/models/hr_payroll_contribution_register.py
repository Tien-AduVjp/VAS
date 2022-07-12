from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from odoo.tools import format_amount


class HRPayrollContributionRegister(models.Model):
    _inherit = 'hr.payroll.contribution.register'

    max_contribution_employee = fields.Monetary(string="Monthly Max. Contribution by Employee", default=0.0, readonly=True, tracking=True,
                                                    states={'draft': [('readonly', False)]},
                                                    help="The maximum amount per month that the employee has to contribute. Leave this zero to disable this limit.")
    max_contribution_company = fields.Monetary(string="Monthly Max. Contribution by Company", default=0.0, readonly=True, tracking=True,
                                                   states={'draft': [('readonly', False)]},
                                                   help="The maximum amount per month that the company has to contribute. Leave this zero to disable this limit.")

    @api.constrains('contribution_base', 'max_contribution_employee', 'max_contribution_company')
    def _check_contribution_amount(self):
        for r in self:
            administrative_region = r.employee_id.contract_id.administrative_region_id or r.employee_id.administrative_region_id
            if administrative_region:
                administrative_region_contribution = r.type_id._get_administrative_region_contribution(administrative_region)
                if administrative_region_contribution.max_contribution_base and administrative_region_contribution.max_contribution_base < r.contribution_base:
                    raise ValidationError(_("Amount %s is greater than the Max. Contribution Base which is %s\nPlease enter an amount less than or equal to this.")
                                          %(format_amount(self.env, r.contribution_base, r.currency_id),
                                            format_amount(self.env, administrative_region_contribution.max_contribution_base, r.currency_id)))
                if administrative_region_contribution.min_contribution_base and administrative_region_contribution.min_contribution_base > r.contribution_base:
                    raise ValidationError(_("Amount %s is less than the Min. Contribution Base which is %s\nPlease enter an amount greater than or equal to this.")
                                          %(format_amount(self.env, r.contribution_base, r.currency_id),
                                            format_amount(self.env, administrative_region_contribution.min_contribution_base, r.currency_id)))
                if administrative_region_contribution.max_contribution_employee and administrative_region_contribution.max_contribution_employee < r.max_contribution_employee:
                    raise ValidationError(_("Amount %s is greater than the Max. Contribution by Employee which is %s\nPlease enter an amount less than or equal to this.")
                                          %(format_amount(self.env, r.max_contribution_employee, r.currency_id),
                                            format_amount(self.env, administrative_region_contribution.max_contribution_employee, r.currency_id)))
                if administrative_region_contribution.max_contribution_company and administrative_region_contribution.max_contribution_company < r.max_contribution_company:
                    raise ValidationError(_("Amount %s is greater than the Max. Contribution by Company which is %s\nPlease enter an amount less than or equal to this.")
                                          %(format_amount(self.env, r.max_contribution_company, r.currency_id),
                                            format_amount(self.env, administrative_region_contribution.max_contribution_company, r.currency_id)))

    def _prepare_history_data(self, date_from, state, date_to=None):
        res = super(HRPayrollContributionRegister, self)._prepare_history_data(date_from, state, date_to)
        res.update({
            'max_contribution_employee': self.max_contribution_employee,
            'max_contribution_company': self.max_contribution_company
        })
        return res
