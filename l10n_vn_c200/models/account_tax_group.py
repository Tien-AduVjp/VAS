from odoo import models


class AccountTaxGroup(models.Model):
    _inherit = 'account.tax.group'

    def set_tax_group_is_vat_vietnam(self):
        tax_group_xml_ids = [
            'l10n_vn.tax_group_0',
            'l10n_vn.tax_group_5',
            'l10n_vn.tax_group_10',
            ]
        account_tax_group_ids = self.env['account.tax.group']
        for xml_id in tax_group_xml_ids:
            account_tax_group_ids |= self.env.ref(xml_id)
        if account_tax_group_ids:
            account_tax_group_ids.write({'is_vat': True})
