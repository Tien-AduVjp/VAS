from odoo import models, api, _


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
                'validation_type': 'both',
                'responsible_id': self.env.ref('base.user_admin').id,
                'company_id': self.id
                }
        
    def _prepare_approval_request_type_vals_list(self):
        vals_list = super(ResCompany, self)._prepare_approval_request_type_vals_list()
        for r in self:
            vals = r._prepare_overtime_approval_request_type_data()
            if bool(vals):
                vals_list.append(vals)
        return vals_list

    def _generate_approval_request_type(self):
        return self.env['approval.request.type'].sudo().create(self._prepare_approval_request_type_vals_list())

