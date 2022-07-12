from odoo import models, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    def _prepare_stock_allocation_approval_request_type_data(self):
        self.ensure_one()
        type_name = _("Stock Allocation Approval")
        existing_request = self.env['approval.request.type'].sudo().search([
            ('company_id', '=', self.id),
            ('name', '=', type_name)
            ], limit=1)
        if existing_request:
            return {}
        else:
            return {
                'name': type_name,
                'type': "stock_allocation",
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
        for r in self:
            vals = r._prepare_stock_allocation_approval_request_type_data()
            if bool(vals):
                vals_list.append(vals)
        return vals_list
