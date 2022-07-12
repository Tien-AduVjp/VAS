from odoo import api, fields, models


class IrTranslation(models.Model):
    _inherit = 'ir.translation'

    @api.model
    def translate_fields(self, model, id, field=None):
        action = super(IrTranslation, self).translate_fields(model, id, field=field)
        # When opening translation dialog to translate the partner's name, it loads values that includes parent values
        # of current record. So we override the translation domain to get its own translation value only.
        # Detail issue: https://viindoo.com/web#id=2993&model=helpdesk.ticket&view_type=form&cids=1&menu_id=
        if model == 'res.partner' and field == 'name':
            action['domain'] = ['&', ('res_id', '=', id), ('name', '=like', model + ',%')]
        return action

    @api.model_create_multi
    def create(self, vals_list):
        res = super(IrTranslation, self).create(vals_list)

        res._update_translations_of_res_partner()
        return res

    def write(self, vals):
        res = super(IrTranslation, self).write(vals)

        self._update_translations_of_res_partner()
        return res

    def _update_translations_of_res_partner(self):
        """ Update the translations of display_name and commercial_company_name fields of records.
        """
        def group_by_lang(trans):
            """This method to process ir.translation records before passing self.env ['res.partner'].create(vals_list)
            :param trans list of ir.translation
            :return: mapping of lang values to the list of res_id
            :rtype: dict
            """
            res = {}
            for tran in trans:
                if tran.name != 'res.partner,name':
                    continue
                if tran.lang in res:
                    res[tran.lang].append(tran.res_id)
                else:
                    res[tran.lang] = [tran.res_id]
            return res

        res = group_by_lang(self)
        for lang in res:
            partners = self.env['res.partner'].browse(res[lang]).exists()
            partners._update_translations_of_res_partner(lang)
