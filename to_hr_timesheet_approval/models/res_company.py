from odoo import models, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    def _prepare_timesheet_approval_request_type_data(self):
        self.ensure_one()
        return {
            'name':  _('Timesheet Approval'),
            'type': 'timesheets',
            'validation_type': 'leader',
            'company_id': self.id
            }
        
    def _prepare_approval_request_type_vals_list(self):
        vals_list = super(ResCompany, self)._prepare_approval_request_type_vals_list()
        RequestType = self.env['approval.request.type'].sudo()
        for r in self:
            vals = r._prepare_timesheet_approval_request_type_data()
            request = RequestType.search([('company_id', '=', r.id), ('type', '=', 'timesheets')], limit=1)
            if not request:
                vals_list.append(vals)
        return vals_list
