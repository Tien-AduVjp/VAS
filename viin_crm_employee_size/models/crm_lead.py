from odoo import fields, models, api


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    employee_size_id = fields.Many2one('res.partner.employee.size',
                                       compute='_compute_employee_size_id',
                                       string='Employee Size',
                                       store=True, readonly=False)

    @api.depends('partner_id')
    def _compute_employee_size_id(self):
        for r in self:
            r.employee_size_id = r.partner_id.commercial_partner_id.employee_size_id

    def _prepare_customer_values(self, partner_name, is_company=False, parent_id=False):
        res = super(CrmLead, self)._prepare_customer_values(partner_name, is_company=is_company, parent_id=parent_id)
        if is_company == True:
            res['employee_size_id'] = self.employee_size_id.id
        return res
