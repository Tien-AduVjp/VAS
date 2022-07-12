from odoo import models


class Respartner(models.Model):
    _inherit = 'res.partner'

    def _find_company(self):
        """
        Find the company that associated with the current partner
        """
        return self.env['res.company'].sudo().search([('partner_id', '=', self.commercial_partner_id.id)], limit=1)

    def _get_inter_comp_user(self):
        company = self._find_company()
        return company.intercompany_user_id or self.env.ref('base.user_root')

