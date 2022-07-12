from odoo import models, api, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    def prepare_procurement_approval_request_type_data(self):
        self.ensure_one()
        return {
            'name':  _("Procurement Approval"),
            'type': "procurement",
            'validation_type': "both",
            'company_id': self.id
            }

    def _generate_procurement_approval_request_type(self):
        Request_type = self.env['approval.request.type'].sudo()
        vals_list = []
        for r in self:
            requests = Request_type.search([('company_id', '=', r.id),('type','=','procurement')])
            if not requests:
                vals_list.append(r.prepare_procurement_approval_request_type_data())
        return Request_type.create(vals_list)

    @api.model
    def create(self, values):
        company = super(ResCompany, self).create(values)
        company.sudo()._generate_procurement_approval_request_type()
        return company