from odoo import models, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    def _prepare_overtime_approval_request_type_data(self):
        self.ensure_one()
        type_name = _("Overtime Approval")
        existing_request = self.env['approval.request.type'].sudo().search([
            ('company_id', '=', self.id),
            ('name', '=', type_name)
            ], limit=1)
        if existing_request:
            return {}
        else:
            return {
                'name': type_name,
                'type': "overtime",
                'manager_approval': 'required',
                'type_approval_user_line_ids':[(0, 0, {
                    'user_id': self.env.ref('base.user_admin').id,
                    'required': True
                })],
                'company_id': self.id,
                'mimimum_approvals': 2
                }

    def _prepare_approval_request_type_vals_list(self):
        vals_list = super(ResCompany, self)._prepare_approval_request_type_vals_list()
        RequestType = self.env['approval.request.type'].sudo()
        for r in self:
            request_type = RequestType.search([('company_id', '=', r.id), ('type', '=', 'overtime')], limit=1)
            if not request_type:
                vals_list.append(r._prepare_overtime_approval_request_type_data())
        return vals_list
