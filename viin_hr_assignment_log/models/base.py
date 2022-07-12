from odoo import models


class Base(models.AbstractModel):
    _inherit = 'base'

    def _prepare_user_assignment_vals(self, date_start=None):
        vals = super(Base, self)._prepare_user_assignment_vals(date_start=date_start)
        if bool(vals):
            # find the employee related to the company of the record
            company = self.company_id if hasattr(self, 'company_id') and self.company_id else self.env.company
            responsible_user_field_name = self._get_responsible_user_field_name()
            user_id = vals.get(responsible_user_field_name, False)
            employee = self.env['res.users'].browse(user_id).sudo().with_company(company).employee_id
            if employee:
                vals['employee_id'] = employee.id
        return vals
