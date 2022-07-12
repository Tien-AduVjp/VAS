from odoo import models, api, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    def _prepare_approval_request_type_data(self):
        self.ensure_one()
        return {
            'name':  _("General Approval"),
            'type': "generic",
            'validation_type': "leader",
            'company_id': self.id
            }
        
    def _prepare_approval_request_type_vals_list(self):
        RequestType = self.env['approval.request.type'].sudo()
        vals_list = []
        for r in self:
            vals = r._prepare_approval_request_type_data()
            request = RequestType.search([('company_id', '=', r.id), ('name', '=', vals.get('name', ''))], limit=1)
            if not request:
                vals_list.append(vals)
        return vals_list

    def _generate_approval_request_type(self):
        return self.env['approval.request.type'].sudo().create(self._prepare_approval_request_type_vals_list())
    
    @api.model_create_multi
    def create(self, vals_list):
        companies = super(ResCompany, self).create(vals_list)
        companies.sudo()._generate_approval_request_type()
        return companies
