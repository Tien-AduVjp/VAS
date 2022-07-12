from odoo import fields, models, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    group_show_line_tax_details = fields.Boolean("Show line tax details",
                                                 implied_group='to_invoice_tax_details.group_show_line_tax_details',
                                                 groups='base.group_portal,base.group_user,base.group_public')
    show_line_subtotals_tax_selection = fields.Selection(selection_add=[('tax_details', 'Tax Details')], ondelete={'tax_details': 'set default'})

    @api.onchange('show_line_subtotals_tax_selection')
    def _onchange_sale_tax(self):
        if self.show_line_subtotals_tax_selection == "tax_details":
            self.update({
                'group_show_line_subtotals_tax_included': False,
                'group_show_line_subtotals_tax_excluded': False,
                'group_show_line_tax_details': True,
            })
        else:
            self.update({
                'group_show_line_tax_details': False,
            })
            super(ResConfigSettings, self)._onchange_sale_tax()
