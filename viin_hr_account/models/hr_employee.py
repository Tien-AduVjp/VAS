from odoo import models, fields


class HrContract(models.Model):
    _inherit = 'hr.employee'

    property_advance_account_id = fields.Many2one('account.account', company_dependent=True,
        string='Advance Account',
        domain="[('internal_type', '=', 'receivable'), ('deprecated', '=', False), ('company_id', '=', current_company_id)]",
        help="If specified, this account will be used for employee advance operations instead of the default receivable account"
        " of the related partner specified by the private address.")

    def _get_payable_account(self):
        self.ensure_one()
        return self.address_home_id.with_company(self.company_id).property_account_payable_id or self.company_id.general_employee_payable_account_id

    def _get_receivable_account(self):
        self.ensure_one()
        return self.with_company(self.company_id).property_advance_account_id or self.address_home_id.with_company(self.company_id).property_account_receivable_id

    def _get_advance_account(self):
        self.ensure_one()
        return self.with_company(self.company_id).property_advance_account_id or self._get_receivable_account()
