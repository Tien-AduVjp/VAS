from odoo import models, api, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    def _prepare_procurement_approval_request_type_data(self):
        self.ensure_one()
        return {
            'name': _("Procurement Approval"),
            'type': "procurement",
            'manager_approval': 'required',
            'type_approval_user_line_ids':[(0, 0, {
                'user_id': self.env.ref('base.user_admin').id,
                'required': True
            })],
            'company_id': self.id,
            'mimimum_approvals': 2
            }

    def _get_procurement_approval_request_type(self):
        return self.env['approval.request.type'].sudo().search([
            ('company_id', 'in', self.ids),
            ('name', '=', _("Procurement Approval"))
            ])

    def _prepare_approval_request_type_vals_list(self):
        vals_list = super(ResCompany, self)._prepare_approval_request_type_vals_list()
        procurement_approval_types = self._get_procurement_approval_request_type()
        for r in self:
            if not procurement_approval_types.filtered(lambda t: t.company_id == r):
                vals_list.append(r._prepare_procurement_approval_request_type_data())
        return vals_list
