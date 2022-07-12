from odoo import models, fields


class AccountTax(models.Model):
    _inherit = 'account.tax'

    is_vat = fields.Boolean(string='Is VAT', related='tax_group_id.is_vat', store=True,
                            help="The value of this field is related to the value of the 'Is VAT' field of the"
                            " corresponding Tax Group set in Advanced Options tab")
