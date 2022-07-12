from odoo import models


class AccountTaxGroup(models.Model):
    _inherit = 'account.tax.group'

    def _set_tax_group_is_vat_vietnam(self):
        tax_group_xml_ids = [
            'l10n_vn.tax_group_0',
            'l10n_vn.tax_group_5',
            'l10n_vn.tax_group_10',
            ]
        tax_groups = self.env['account.tax.group']
        for xml_id in tax_group_xml_ids:
            tax_groups |= self.env.ref(xml_id)
        if tax_groups:
            tax_groups.write({'is_vat': True})
