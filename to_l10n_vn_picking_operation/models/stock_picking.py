from odoo import models, fields, api, _


class Picking(models.Model):
    _name = 'stock.picking'
    _inherit = ['stock.picking', 'to.vietnamese.number2words']

    footer_date = fields.Char(string='Footer Date', compute='_compute_footer_date')
    total_amount_untaxed = fields.Monetary(string='Total Amount Untaxed', compute='_compute_total_amount_untaxed',
                                           help="Use to print PDF Picking Operation")
    total_amount_untaxed_in_words = fields.Char(string='Total Amount Untaxed In Words', compute='_compute_total_amount_untaxed_in_words',
                                                help="Use to show Total Amount by Words when print PDF Picking Operation")
    currency_id = fields.Many2one('res.currency', related='company_id.currency_id')
    attached_docs = fields.Char(string='Attached Docs',
                                help="Reference of Source/Related documents, if any, that are attached to this documents for printing purpose.")
    debit_code = fields.Char(string='Debit Acc.', compute='_compute_debit_credit_code', compute_sudo=True)
    credit_code = fields.Char(string='Credit Acc.', compute='_compute_debit_credit_code', compute_sudo=True)
    reason = fields.Char(string='Reason', compute='_compute_reason', help="Technical field that will be printed on pricking operation sheets")

    @api.depends('date_done')
    def _compute_footer_date(self):
        for r in self:
            year, month, day = self.env['to.base'].split_date(r.date_done or fields.Date.today())
            r.footer_date = _("Ngày %s tháng %s năm %s") % (day, month, year)

    @api.depends('move_lines.price_unit', 'move_lines.quantity_done', 'move_lines.product_uom_qty')
    def _compute_total_amount_untaxed(self):
        for r in self:
            total_amount_untaxed = 0.0
            for move in r.move_lines:
                qty = move.quantity_done if r.state == 'done' else move.product_uom_qty
                total_amount_untaxed += move._get_price_unit_currency_conversion() * qty
            r.total_amount_untaxed = total_amount_untaxed

    @api.depends('total_amount_untaxed', 'company_id.currency_id')
    def _compute_total_amount_untaxed_in_words(self):
        for r in self:
            r.total_amount_untaxed_in_words = r.num2words(r.total_amount_untaxed, precision_rounding=r.company_id.currency_id.rounding)

    @api.depends('account_move_ids.line_ids.debit', 'account_move_ids.line_ids.credit')
    def _compute_debit_credit_code(self):
        for r in self:
            lines = r.account_move_ids.mapped('line_ids')
            debit_code = False
            credit_code = False
            if lines:
                debit_lines = lines.filtered(lambda l: l.debit > 0)
                credit_lines = lines.filtered(lambda l: l.credit > 0)
                debit_code = ", ".join(debit_lines.mapped('account_id.code'))
                credit_code = ", ".join(credit_lines.mapped('account_id.code'))
            r.debit_code = debit_code
            r.credit_code = credit_code

    @api.depends('purchase_id.date_order', 'sale_id.date_order', 'group_id', 'origin')
    def _compute_reason(self):
        for r in self:
            if r.purchase_id:
                year, month, day = self.env['to.base'].split_date(r.purchase_id.date_order)
                reason = _("Theo đơn mua %s, đặt hàng ngày %s tháng %s năm %s") % (r.purchase_id.name, day, month, year)
            elif r.sale_id:
                year, month, day = self.env['to.base'].split_date(r.sale_id.date_order)
                reason = _("Theo đơn bán %s, xác nhận ngày %s tháng %s năm %s") % (r.sale_id.name, day, month, year)
            elif r.group_id:
                reason = _("Theo tài liệu %s") % r.group_id.name
            elif r.origin:
                reason = _("Theo tài liệu %s") % r.origin
            else:
                reason = False
            r.reason = reason
