from odoo import fields, models


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    inter_comp_invoice_line_id = fields.Many2one('account.move.line', string='Inter-Company Invoice Line', readonly=True, copy=False)

    def _prepare_intercomp_invoice_line_data(self):
        self.ensure_one()
        data = {
            'name': self.name,
            'price_unit': self.price_unit,
            'quantity': self.quantity,
            'discount': self.discount,
            'product_id': self.product_id.id or False,
            'product_uom_id': self.product_uom_id.id or False,
            'sequence': self.sequence,
            'inter_comp_invoice_line_id': self.id
        }
        if self.analytic_account_id and not self.analytic_account_id.company_id:
            data['analytic_account_id'] = self.analytic_account_id.id
        analytic_tags = []
        for tag in self.analytic_tag_ids.filtered(lambda t: not t.company_id):
            analytic_tags.append((4, tag.id))
        if analytic_tags:
            data['analytic_tag_ids'] = analytic_tags
        return data
