from odoo import models


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    def _prepend_vietnamese_description_to_name(self):
        for r in self.filtered(lambda line: line.product_id).with_context(lang=self.env.ref('base.lang_vi_VN').code):
            new_invoice_line_name = r.product_id.description_sale or r.product_id.name
            new_invoice_line_name += ' (%s)' % r.name
            r.name = r.standardize_einvoice_item_name(new_invoice_line_name)
