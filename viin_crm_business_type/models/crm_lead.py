from odoo import fields, models, api


class CrmLead(models.Model):
    _inherit = 'crm.lead'

    business_type_id = fields.Many2one('res.partner.business.type', string='Business Type',
                                       compute='_compute_business_type_id', store=True,
                                       readonly=False)

    @api.depends('partner_id')
    def _compute_business_type_id(self):
        for r in self:
            r.business_type_id = r.partner_id.commercial_partner_id.business_type_id

    def _prepare_customer_values(self, partner_name, is_company=False, parent_id=False):
        res = super(CrmLead, self)._prepare_customer_values(partner_name, is_company=is_company, parent_id=parent_id)
        if is_company == True:
            res['business_type_id'] = self.business_type_id.id
        return res
