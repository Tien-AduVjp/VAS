from odoo import models, fields

class AccountTaxGroup(models.Model):
    _inherit = 'account.tax.group'
    
    is_vat = fields.Boolean(string='Is VAT', help="Check this to indicate that this tax group is for grouping Value Added Taxes."
                            " All taxes belong to this group will hence be value added taxes")
    