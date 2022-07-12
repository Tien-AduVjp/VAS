from odoo import api, models


class Repair(models.Model):
    _inherit = 'repair.order'

    @api.depends('pricelist_id.currency_id', 'partner_id')
    def _amount_tax(self):
        for r in self:
            amount_tax = 0.0

            def tax_cal(repair_line):
                price_reduce = repair_line.price_unit * (1.0 - repair_line.discount / 100.0)
                return repair_line.tax_id.compute_all(price_reduce, r.pricelist_id.currency_id, repair_line.product_uom_qty, repair_line.product_id, r.partner_id)

            for operation in r.operations:
                if operation.tax_id:
                    tax_calculate = tax_cal(operation)
                    for tc in tax_calculate['taxes']:
                        amount_tax += tc['amount']
            for fee in r.fees_lines:
                if fee.tax_id:
                    tax_calculate = tax_cal(fee)
                    for tc in tax_calculate['taxes']:
                        amount_tax += tc['amount']
            r.amount_tax = amount_tax

    def _create_invoices(self, group=False):
        res = super(Repair, self)._create_invoices(group=group)
        self = self.with_context({'check_move_validity': False})
        invoiced_orders = self.filtered(lambda ro: ro.state not in ('draft', 'cancel') and ro.invoice_id)
        for r in invoiced_orders:
            for operation in r.operations:
                if operation.invoice_line_id:
                    operation.invoice_line_id.discount = operation.discount
            for fee in r.fees_lines:
                if fee.invoice_line_id:
                    fee.invoice_line_id.discount = fee.discount
        invoiced_orders.invoice_id._recompute_dynamic_lines(recompute_all_taxes=True)
        return res
