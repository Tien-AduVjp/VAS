from odoo import fields, models
    
class ResBank(models.Model):
    _inherit = 'res.bank'
    
    name = fields.Char(translate=True)
    street = fields.Char(translate=True)
    street2 = fields.Char(translate=True)
    city = fields.Char(translate=True)
    
class ResPartnerPank(models.Model):
    _inherit = 'res.partner.bank'
    
    bank_name = fields.Char(translate=True)
    owner_name = fields.Char(translate=True)
    street = fields.Char(translate=True)
    city = fields.Char(translate=True)  

class ResCountryState(models.Model):
    _inherit = 'res.country.state'
    
    name = fields.Char(translate=True)

class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    name = fields.Char(translate=True)
    display_name = fields.Char(translate=True)
    street = fields.Char(translate=True)
    street2 = fields.Char(translate=True)
    city = fields.Char(translate=True)
    commercial_company_name = fields.Char(translate=True)

    def write(self, vals):
        res = super(ResPartner, self).write(vals)
        if 'name' in vals and 'lang' in self.env.context:
            self._update_translations_of_res_partner(self.env.context['lang'])
        return res

    def _update_translations_of_res_partner(self, lang):
        """ Update the translations of display_name and commercial_company_name fields of records.
        """
        for r in self:
            commercial_partner_id = r.commercial_partner_id
            if commercial_partner_id.is_company:
                # we need to clear the cache before get name's value of commercial_partner_id
                commercial_partner_id.invalidate_cache(fnames=['name'], ids=commercial_partner_id.ids)

                source_value = fields.first(commercial_partner_id.with_context(lang=None))['name']
                dest_value = commercial_partner_id.with_context(lang=lang).name
    
                self.env['ir.translation']._set_ids(
                    'res.partner,commercial_company_name', 'model', lang, r._ids, dest_value, source_value,
                )
                # we need to clear the cache before recompute the translation of display_name of self
                r.invalidate_cache(fnames=['commercial_company_name'], ids=r.ids)

            source_value = fields.first(r.with_context(lang=None))['display_name']

            diff = dict(show_address=None, show_address_only=None, show_email=None, html_format=None, show_vat=None, lang=lang)
            names = dict(r.with_context(**diff).name_get())
            dest_value = names.get(r.id, '')

            self.env['ir.translation']._set_ids(
                'res.partner,display_name', 'model', lang, r._ids, dest_value, source_value,
            )
            # Update the translations of display_name and commercial_company_name fields of child records
            if r.child_ids:
                r.child_ids._update_translations_of_res_partner(lang)


class ResCompany(models.Model):
    _inherit = 'res.company'    
    
    name = fields.Char(translate=True)
    street = fields.Char(translate=True)
    street2 = fields.Char(translate=True)
    city = fields.Char(translate=True)
