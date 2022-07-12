from odoo import models, fields

class AccountJournal(models.Model):
    _inherit = 'account.journal'

    invoice_line_summary_group_mode = fields.Selection([('product_unit_price_tax_discount','Product, Unit price, Tax, Discount'),
                                   ('product_tax_discount','Product, Tax, Discount'),
                                   ('product_template_unit_price_tax_discount','Product template, Unit price, Tax, Discount'),
                                   ('product_template_tax_discount','Product template, Tax, Discount'),
                                   ],
                                    default='product_unit_price_tax_discount',
                                    help='if have an setting: create Billing will get default mode in journal else create Billing will get default mode in company',
                                    string='Default Summary Line Mode')

    invoice_display_mode = fields.Selection([('invoice_lines', 'Invoice Lines'),
                                           ('invoice_line_summary_lines', 'Invoice Line Summary Lines')],
                                            default='invoice_lines',
                                            help='Select option invoice display mode, This change will change the all display "invoice line". for example: portal, pdf, preview ...',
                                            string='Default Invoice Display Mode')
