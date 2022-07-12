from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class CustomDeclarationTaxExport(models.Model):
    _name = "custom.declaration.tax.export"
    _inherit = 'abstract.custom.declaration.tax'
    _description = "Custom Declaration Export Tax"

    custom_declaration_id = fields.Many2one('custom.declaration.export', string='Export Custom Declaration',
                                            ondelete='cascade', index=True, required=True)
    partner_id = fields.Many2one(related='custom_declaration_id.partner_id', store=True)
    custom_dec_tax_group_id = fields.Many2one('custom.declaration.tax.export.group', string='Custom Declaration Tax Group', readonly=True)

    def _compute_amount_tax(self):
        for r in self:
            amount = 0.0
            taxes = r.custom_declaration_id.custom_declaration_line_ids.get_taxes_values()
            for tax in taxes:
                if tax['product_id'] == r.product_id.id and tax['tax_id'] == r.tax_id.id:
                    amount = tax['currency_amount_tax']
            r.amount = amount
    
    @api.depends('custom_declaration_id')
    def _compute_currency(self):
        for r in self:
            if r.custom_declaration_id:
                r.currency_id = r.custom_declaration_id.currency_id
                r.currency_rate = r.custom_declaration_id.currency_rate
                r.company_id = r.custom_declaration_id.company_id
            else:
                r.currency_id = False
                r.currency_rate = 1.0
                r.company_id = False
    
    def _prepare_account_move_lines(self):
        ref = "(%s) %s - %s" % (self.custom_declaration_id.name, self.product_id.name, self.name)
        partner_id = self.partner_id.id or False
        res = []

        if self.is_vat:
            if not self.tax_repartition_line_id.vat_ctp_account_id:
                raise ValidationError(_("Please specify VAT counterpart account for the tax '%s'.") % (self.tax_id.name,))
            account_id = self.tax_repartition_line_id.vat_ctp_account_id
        else:
            account_id = self.product_id.product_tmpl_id._get_product_accounts()['income']
            if not account_id:
                raise ValidationError(_("Cannot find any income account specified for the product '%s' nor the product category '%s'.")
                                % (self.product_id.name, self.product_id.categ_id.name))

        if self.payment_term_id:
            totlines = self.payment_term_id.with_context(currency_id=self.custom_declaration_id.currency_id.id).compute(self.currency_amount_tax, fields.Date.today())[0]
            date_maturity = totlines[0]
        else:
            date_maturity = fields.Date.today()

        # product line
        res.append((0, 0, {
                'product_id': self.product_id.id,
                'date_maturity': self.custom_declaration_id.clearance_date or self.custom_declaration_id.request_date,
                'partner_id': partner_id,
                'name': ref,
                'debit': self.amount,
                'credit': 0,
                'account_id': account_id.id,
                'analytic_account_id':self.custom_declaration_line_id.account_analytic_id.id,
                'analytic_tag_ids':[(6, 0, self.custom_declaration_line_id.analytic_tag_ids.ids)],
                'tax_ids': [(4, self.tax_id.id)],
                'ref': ref,
                'quantity': 1,
            }))
            # tax line
        res.append((0, 0, {
            'date_maturity': date_maturity,
            'partner_id': partner_id,
            'name': ref,
            'debit': 0,
            'credit': self.amount,
            'account_id': self.tax_repartition_line_id.account_id.id,
            'tax_repartition_line_id': self.tax_repartition_line_id.id,
            'ref': ref,
            'quantity': 1,
        }))
        return res

    def _get_custom_dec_tax_group_model(self):
        return 'custom.declaration.tax.export.group'
