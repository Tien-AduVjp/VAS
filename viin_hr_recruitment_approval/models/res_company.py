from odoo import models, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    def _prepare_recruitment_approval_request_type_data(self):
        self.ensure_one()
        type_name = _('Recruitment Approval')
        existing_request = self.env['approval.request.type'].sudo().search([
            ('company_id', '=', self.id),
            ('name', '=', type_name)
            ], limit=1)
        if existing_request:
            return {}
        return {
            'name': type_name,
            'type': 'recruitment',
            'manager_approval': 'required',
            'sequential_approvals': True,
            'type_approval_user_line_ids':[(0, 0, {
                    'user_id': self.env.ref('base.user_admin').id,
                    'required': True
                }
            )],
            'mimimum_approvals': 2,
            'company_id': self.id
            }

    def _prepare_approval_request_type_vals_list(self):
        vals_list = super(ResCompany, self)._prepare_approval_request_type_vals_list()
        for r in self:
            vals = r._prepare_recruitment_approval_request_type_data()
            if vals:
                vals_list.append(vals)
        return vals_list

    def _generate_approval_request_type(self):
        return self.env['approval.request.type'].sudo().create(self._prepare_approval_request_type_vals_list())
