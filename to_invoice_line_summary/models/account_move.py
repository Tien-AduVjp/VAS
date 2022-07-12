from itertools import groupby

from odoo import models, fields, api,_


class AccountMove(models.Model):
    _inherit = "account.move"

    invoice_line_summary_ids = fields.One2many('invoice.line.summary', 'invoice_id', string='Summary Lines',
                                               compute='_compute_invoice_line_summary_ids',
                                               store=True, groups='account.group_account_invoice')
    # it was `invoice_line_summary_mode` in 13.0
    invoice_line_summary_group_mode = fields.Selection([('product_unit_price_tax_discount','Product, Unit price, Tax, Discount'),
                               ('product_tax_discount','Product, Tax, Discount'),
                               ('product_template_unit_price_tax_discount','Product template, Unit price, Tax, Discount'),
                               ('product_template_tax_discount','Product template, Tax, Discount'),
                               ],  help='Select style option invoice line summary display mode',
                                   string='Invoice Summary Line Mode',
                                   compute='_compute_default_summary_mode', store=True, readonly=False)
    invoice_display_mode = fields.Selection([('invoice_lines', 'Invoice Lines'),
                                           ('invoice_line_summary_lines', 'Invoice Line Summary Lines')],
                                           help='Select option invoice display mode, This change will change the all display "invoice line". for example: portal, pdf, preview ...',
                                           string='Invoice Display Mode',
                                           compute='_compute_default_summary_mode', store=True, readonly=False)

    @api.depends('journal_id')
    def _compute_default_summary_mode(self):
        for r in self:
            r.invoice_line_summary_group_mode = r.journal_id.invoice_line_summary_group_mode
            r.invoice_display_mode = r.journal_id.invoice_display_mode

    @api.model_create_multi
    def create(self, vals_list):
        Journal = self.env['account.journal']
        for val in vals_list:
            journal = Journal.browse(val.get('journal_id', False))
            if not journal.exists():
                move_type = 'entry'
                if val.get('move_type', False):
                    move_type = val['move_type']
                elif self._context.get('default_move_type', False):
                    move_type = self._context['default_move_type']
                journal = self.env['account.move'].with_context(default_move_type= move_type)._get_default_journal()
                val.setdefault('journal_id',journal.id)
            val.setdefault('invoice_line_summary_group_mode',journal.invoice_line_summary_group_mode)
            val.setdefault('invoice_display_mode',journal.invoice_display_mode)
        res = super(AccountMove, self).create(vals_list)
        return res

    @api.depends('invoice_line_summary_group_mode', 'invoice_line_ids.product_id',
                 'invoice_line_ids.quantity', 'invoice_line_ids.price_unit', 'invoice_line_ids.discount',
                 'invoice_line_ids.tax_ids', 'invoice_line_ids.product_uom_id')
    def _compute_invoice_line_summary_ids(self):
        prec_product_price = self.env['decimal.precision'].precision_get('Product Price')
        AccountMoveLine = self.env['account.move.line']
        for r in self:
            vals_list = [(5, 0, 0)]
            if r.move_type in self.get_invoice_types():
                invoice_lines_with_product = r.invoice_line_ids.filtered(lambda line: line.product_id).sorted(key=lambda r: r.product_id.id)
                invoice_lines_without_product = r.invoice_line_ids - invoice_lines_with_product
                same_invoice_lines = []
                # list keys to group invoice lines
                group_keys = ['tax_ids', 'discount']
                if r.invoice_line_summary_group_mode in ('product_unit_price_tax_discount', 'product_tax_discount'):
                    group_keys.append('product_id')
                else:
                    group_keys.append('product_id.product_tmpl_id')
                for keys, group_invoice_lines in groupby(
                    invoice_lines_with_product,
                    lambda line: [line.mapped(key) for key in group_keys]
                    ):
                    group_invoice_lines = AccountMoveLine.browse(h.id for h in group_invoice_lines)
                    if r.invoice_line_summary_group_mode in ('product_unit_price_tax_discount', 'product_template_unit_price_tax_discount'):
                        for invoice_line in group_invoice_lines:
                            if invoice_line.product_uom_id:
                                group_invoice_line = group_invoice_lines.filtered(
                                    lambda line: fields.Float.compare(
                                        line.price_unit,
                                        invoice_line.product_uom_id._compute_price(
                                            invoice_line.price_unit,
                                            line.product_uom_id
                                            ),
                                        precision_digits=prec_product_price
                                        ) == 0
                                    )
                            else:
                                group_invoice_line = group_invoice_lines.filtered(
                                    lambda line: fields.Float.compare(
                                        line.price_unit,
                                        invoice_line.price_unit,
                                        precision_digits=prec_product_price
                                        ) == 0
                                    )
                            if group_invoice_line:
                                same_invoice_lines.append(group_invoice_line)
                                group_invoice_lines -= group_invoice_line
                        continue
                    same_invoice_lines.append(group_invoice_lines)

                # group invoice line without product
                for invoice_line in invoice_lines_without_product:
                    same_invoice_lines.append(invoice_line)
                for invoice_lines in same_invoice_lines:
                    vals_list.append((0, 0, {'invoice_line_ids': invoice_lines}))
            r.invoice_line_summary_ids = vals_list
