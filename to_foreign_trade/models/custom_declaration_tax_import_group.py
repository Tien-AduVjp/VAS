from odoo import fields, models


class CustomDeclarationTaxImportGroup(models.Model):
    _name = 'custom.declaration.tax.import.group'
    _inherit = 'abstract.custom.declaration.tax.group'
    _description = "Custom Declaration Import Tax Group"

    custom_declaration_id = fields.Many2one('custom.declaration.import', string='Import Custom Declaration',
                                            ondelete='cascade', index=True, required=True)
    custom_declaration_tax_line_ids = fields.One2many('custom.declaration.tax.import', 'custom_dec_tax_group_id', string='Tax Lines', readonly=True)
