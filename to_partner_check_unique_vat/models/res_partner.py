from odoo import models, api, _, fields
from odoo.exceptions import UserError


class ResPartner(models.Model):
    _inherit = 'res.partner'

    vat =  fields.Char(copy=False)

    @api.constrains('vat', 'parent_id', 'company_id')
    def _check_unique_vat(self):
        records_to_check = self.filtered(
            lambda r: r.vat and (r.company_id.check_unique_vat or (self.env.company.check_unique_vat and not r.company_id))
        )

        records_to_check._compute_same_vat_partner_id()
        for r in records_to_check:
            if r.same_vat_partner_id:
                raise UserError(_("This Tax ID already exists and is being used by Partner '%s'. "
                                  "Please use another VAT code, which is unique!") % r.same_vat_partner_id.name)
