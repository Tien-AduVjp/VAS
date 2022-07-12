from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class AccountInvoiceLineGroup(models.Model):
    _name = "invoice.line.summary"
    _description = 'Invoice Lines Summary'

    name = fields.Char(string='Label', compute='_compute_name', store=True)
    sequence = fields.Integer(string="Sequence", default=10)
    invoice_id = fields.Many2one('account.move', string="Invoice", related='invoice_line_ids.move_id',
                                 store=True, readonly=True, ondelete='cascade')
    invoice_line_ids = fields.One2many('account.move.line', 'invoice_line_summary_id', required=True, readonly=True)

    product_id = fields.Many2one('product.product', string="Product", compute='_compute_product')
    uom_id = fields.Many2one('uom.uom', string="Unit of Measure", compute='_compute_uom')
    quantity = fields.Float(string="Quantity", digits='Product Unit of Measure', compute='_compute_quantity')
    price_unit = fields.Float(string="Price Unit", digits='Product Price', compute='_compute_price_unit')
    price_subtotal = fields.Monetary(string="Price Subtotal", compute='_compute_price', help="Total amount without taxes")
    price_total = fields.Monetary(string="Price Total", compute='_compute_price', help="Total amount with taxes")
    currency_id = fields.Many2one(related='invoice_id.currency_id', readonly=True)
    invoice_line_tax_ids = fields.Many2many('account.tax', string="Taxes", compute='_compute_invoice_line_tax_ids')
    discount = fields.Float(string="Discount", compute='_compute_discount', digits='Discount')
    product_tmpl_id = fields.Many2one("product.template", string="Product Template", compute='_compute_product')
    display_type = fields.Selection(related='invoice_line_ids.display_type')

    @api.depends('invoice_line_ids.name')
    def _compute_name(self):
        for r in self:
            if r.invoice_line_ids:
                if 'product_template' in r.invoice_id.invoice_line_summary_group_mode and not r.display_type:
                    r.name = r.invoice_line_ids[0].product_id.product_tmpl_id.name
                else:
                    r.name = r.invoice_line_ids[0].name
            else:
                r.name = False

    @api.depends('invoice_line_ids.product_uom_id', 'product_id')
    def _compute_uom(self):
        for r in self:
            uoms = r.invoice_line_ids.mapped('product_uom_id')
            referenced_uom = uoms.filtered(lambda uom: uom.uom_type == 'reference')[:1]
            r.uom_id = referenced_uom or uoms[:1]

    @api.depends('invoice_line_ids.product_id', 'invoice_line_ids.product_id.product_tmpl_id')
    def _compute_product(self):
        for r in self:
            products = r.invoice_line_ids.with_context(active_test=False).mapped('product_id')
            r.product_id = products[:1]
            r.product_tmpl_id = products[:1].product_tmpl_id

    @api.depends('invoice_line_ids.quantity', 'invoice_line_ids.product_uom_id', 'product_id', 'uom_id')
    def _compute_quantity(self):
        for r in self:
            qty = 0.0
            if r.invoice_id.invoice_line_summary_group_mode in ('product_tax_discount', 'product_template_tax_discount'):
                r.quantity = sum(r.invoice_line_ids.mapped('quantity'))
            else:
                for ivl in r.invoice_line_ids:
                    qty += ivl.product_uom_id._compute_quantity(ivl.quantity, r.uom_id)
                r.quantity = qty

    @api.depends('product_id', 'invoice_line_ids.price_unit', 'uom_id', 'invoice_line_ids.product_uom_id', 'invoice_line_ids.quantity')
    def _compute_price_unit(self):
        for r in self:
            price_unit = 0.0
            if r.invoice_line_ids:
                price = 0.0
                for invl in r.invoice_line_ids:
                    if invl.product_uom_id and r.uom_id:
                        converted_qty = invl.product_uom_id._compute_quantity(invl.quantity, r.uom_id)
                        converted_price = invl.product_uom_id._compute_price(invl.price_unit, r.uom_id)
                        price += converted_price * converted_qty
                    else:
                        price += invl.price_unit * invl.quantity
                if r.quantity != 0.0:
                    price_unit = price / r.quantity
                else:
                    price_unit = 0.0
            r.price_unit = price_unit

    def _compute_price(self):
        price_data = self.env['account.move.line'].read_group([('invoice_line_summary_id', 'in', self.ids)], ['price_subtotal', 'price_total'], ['invoice_line_summary_id'])
        mapped_data = dict([(group_dict['invoice_line_summary_id'][0], {'price_subtotal': group_dict['price_subtotal'], 'price_total':group_dict['price_total']}) for group_dict in price_data])
        for r in self:
            data = mapped_data.get(r.id, {})
            r.update({
                'price_subtotal': data.get('price_subtotal', 0.0),
                'price_total': data.get('price_total', 0.0),
                })

    @api.depends('invoice_line_ids.tax_ids')
    def _compute_invoice_line_tax_ids(self):
        for r in self:
            r.invoice_line_tax_ids = r.invoice_line_ids.mapped('tax_ids')

    @api.depends('invoice_line_ids.discount')
    def _compute_discount(self):
        for r in self:
            # invoice lines of this line summary always have the same discount
            if r.invoice_line_ids:
                r.discount = r.invoice_line_ids[0].discount
            else:
                r.discount = 0
