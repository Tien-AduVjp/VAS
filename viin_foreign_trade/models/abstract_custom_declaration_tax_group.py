from odoo import fields, models


class CustomDeclarationTaxGroup(models.AbstractModel):
    _name = 'abstract.custom.declaration.tax.group'
    _rec_name = 'tax_group_id'
    _description = "Custom Declaration Tax Group Abstract"

    tax_group_id = fields.Many2one('account.tax.group', string='Tax Group', required=True)
    is_vat = fields.Boolean(string='Is VAT', related='tax_group_id.is_vat')
    company_currency_id = fields.Many2one('res.currency', readonly=True, string='Company Currency',
                                          help='Utility field to express amount currency', store=True)
    amount = fields.Monetary(string="Tax Amount", compute='_compute_amount', currency_field='company_currency_id')

    def _compute_amount(self):
        for r in self:
            r.amount = sum(r.custom_declaration_tax_line_ids.mapped('amount'))
