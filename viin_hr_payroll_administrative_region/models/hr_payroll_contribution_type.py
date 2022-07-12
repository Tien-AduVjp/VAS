from odoo import models, fields, api, _


class HRPayrollContributionType(models.Model):
    _inherit = 'hr.payroll.contribution.type'

    admin_region_payroll_contrib_ids = fields.One2many('admin.region.payroll.contrib', 'payroll_contribution_type_id',
                                                                     string="Administrative Region Payroll Contribution")

    def _prepare_payroll_contribution_register_data(self, contract):
        res = super(HRPayrollContributionType, self)._prepare_payroll_contribution_register_data(contract)
        contribution_amount = self._get_payroll_contribution_amount(contract)
        res.update({
            'contribution_base': contribution_amount.get('contribution_base', 0.0),
            'max_contribution_employee': contribution_amount.get('max_contribution_employee', 0.0),
            'max_contribution_company': contribution_amount.get('max_contribution_company', 0.0)
        })
        return res
        
    def _get_payroll_contribution_amount(self, contract):
        self.ensure_one()        
        contribution_base = contract._get_payroll_contribution_base()
        data = {
            'contribution_base': contribution_base
        }
        
        administrative_region = contract.administrative_region_id or contract.employee_id.administrative_region_id
        administrative_region_contribution = self._get_administrative_region_contribution(administrative_region)
        if administrative_region_contribution:
            data.update({
                'contribution_base': administrative_region_contribution._qualify_contribution_base(contribution_base),
                'max_contribution_employee': administrative_region_contribution.max_contribution_employee,
                'max_contribution_company': administrative_region_contribution.max_contribution_company
            })
        return data

    def _get_administrative_region_contribution(self, administrative_region):
        """
        Get Administrative Region Payroll Contribution by Administrative Region
        """
        self.ensure_one()
        return self.admin_region_payroll_contrib_ids.filtered(lambda r: r.administrative_region_id == administrative_region)
