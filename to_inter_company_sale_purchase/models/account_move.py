from odoo import models


class AccountMove(models.Model):
    _inherit = 'account.move'

    def _generate_inter_comp_invoice(self):
        self.ensure_one()
        invoice = super(AccountMove, self)._generate_inter_comp_invoice()
        inter_comp_user = self.partner_id._get_inter_comp_user()
        if invoice:
            sale_order_line_ids = self.mapped('invoice_line_ids.sale_line_ids')
            for line in sale_order_line_ids:
                if line.inter_comp_purchase_order_line_id and line.invoice_lines:
                    line.sudo(inter_comp_user.id).inter_comp_purchase_order_line_id.invoice_lines = line.invoice_lines.mapped('inter_comp_invoice_line_id')
            purchase_order_lines = self.mapped('invoice_line_ids.purchase_line_id')
            for line in purchase_order_lines:
                if line.inter_comp_sale_order_line_id and line.invoice_lines:
                    line.sudo(inter_comp_user.id).inter_comp_sale_order_line_id.invoice_lines = line.invoice_lines.mapped('inter_comp_invoice_line_id')
        return invoice

