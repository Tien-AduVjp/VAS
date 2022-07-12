from odoo import models, api
from odoo.osv import expression


class CRMLead(models.Model):
    _inherit = 'crm.lead'

    @api.model_create_multi
    def create(self, vals_list):
        records = super(CRMLead, self).create(vals_list)
        records.filtered(lambda r: not r.partner_id)._recognize_partner()
        return records

    def action_recognize_partner(self):
        self._recognize_partner()

    def _recognize_partner(self):
        domain = self._get_recognize_partner_domain()
        partners = self.env['res.partner'].search(domain)
        for r in self:
            recognized_partners = r._match_partners(partners)
            if recognized_partners:
                r.partner_id = recognized_partners[-1:]

    def _get_partner_matching_criteria(self):
        """
        Return
        list: (lead_field, partner_field)
            List of tuples with lead field mapped with partner field
        """
        return [
            ('email_from', 'email'),
            ('phone', 'phone'),
            ('mobile', 'mobile')
        ]

    def _get_recognize_partner_domain(self):
        """
        Return
        list: domain
            Domain for matched criteria partners
        """
        domain = []
        criteria_fields = self._get_partner_matching_criteria()
        for lead_field, partner_field in criteria_fields:
            criteria = self.filtered(lambda r: getattr(r, lead_field)).mapped(lead_field)
            domain.append([(partner_field, 'in', criteria)])
        domain = expression.OR(domain)
        return domain

    def _match_partners(self, partners):
        self.ensure_one()
        match_partners = self.env['res.partner']
        criteria_fields = self._get_partner_matching_criteria()
        for lead_field, partner_field in criteria_fields:
            lead_field_val = getattr(self, lead_field)
            if lead_field_val:
                match_partners = partners.filtered(lambda p: getattr(p, partner_field) == lead_field_val)
                if match_partners:
                    break
        return match_partners
