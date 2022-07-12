from odoo import fields, models

class CustomDeclarationTaxExportGroup(models.Model):
    _name = 'custom.declaration.tax.export.group'
    _inherit = 'abstract.custom.declaration.tax.group'
    _description = "Custom Declaration Export Tax Group"

    custom_declaration_id = fields.Many2one('custom.declaration.export', string='Export Custom Declaration',
                                            ondelete='cascade', index=True, required=True)
    custom_declaration_tax_line_ids = fields.One2many('custom.declaration.tax.export', 'custom_dec_tax_group_id', string='Tax Lines', readonly=True)
