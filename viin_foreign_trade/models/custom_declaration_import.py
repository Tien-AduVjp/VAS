from odoo import models, api, fields, _
from odoo.exceptions import ValidationError, UserError
from odoo.tools import float_is_zero, float_compare

class CustomDeclarationImport(models.Model):
    _name = 'custom.declaration.import'
    _description = 'Import Custom Declaration'
    _inherit = ['abstract.custom.declaration', 'mail.thread', 'mail.activity.mixin']

    purchase_order_ids = fields.Many2many('purchase.order', string='Purchase Orders', domain=[('state', 'in', ['purchase', 'done']), ('foreign_trade', '=', True)],
                                        readonly=True, states={'draft': [('readonly', False)]})

    custom_declaration_line_ids = fields.One2many('custom.declaration.line', 'custom_declaration_import_id', string="Request Line", readonly=False,
                               states={'confirm': [('readonly', True)],
                                       'done': [('readonly', True)],
                                       'cancel': [('readonly', True)]})
    tax_line_ids = fields.One2many('custom.declaration.tax.import', 'custom_declaration_id', string='Tax Lines', readonly=False,
                               states={'confirm': [('readonly', True)],
                                       'done': [('readonly', True)],
                                       'cancel': [('readonly', True)]})
    custom_dec_tax_group_ids = fields.One2many('custom.declaration.tax.import.group', 'custom_declaration_id', string='Tax Groups', readonly=True)
    account_move_ids = fields.One2many('account.move', 'custom_declaration_import_id', string="Journal Entries", readonly=True)
    account_moves_count = fields.Integer(string='# of moves', compute='_compute_move_count')
    payment_term_id = fields.Many2one('account.payment.term', string="Tax Payment Term",
                                      compute='_compute_payment_term_id', readonly=False, store=True,
                                      states={'open': [('readonly', True)],
                                              'confirm': [('readonly', True)],
                                              'done': [('readonly', True)],
                                              'cancel': [('readonly', True)]})
    landed_cost_ids = fields.One2many('stock.landed.cost', 'custom_declaration_import_id', string='Landed Cost')
    landed_cost_count = fields.Integer(string='landed Cost Count', compute='_compute_landed_cost_count', compute_sudo=True)
    extra_expense_ids = fields.One2many('custom.declaration.line.extra.expense', 'custom_declaration_import_id', string='Extra Expenses', readonly=False,
                                        states={'confirm': [('readonly', True)],
                                                'done': [('readonly', True)],
                                                'cancel': [('readonly', True)]})

    @api.depends('landed_cost_ids')
    def _compute_landed_cost_count(self):
        for r in self:
            r.landed_cost_count = len(r.landed_cost_ids)

    @api.constrains('purchase_order_ids', 'stock_picking_ids')
    def _check_po_vs_picking(self):
        for r in self:
            # check po, which doesn't have same partner
            if not r._check_po_same_partner():
                raise ValidationError(_("The selected purchase order(s) doesn't have same vendor."))

            # check po, which doesn't have same currency
            if not r._check_po_same_currency():
                raise ValidationError(_("The selected purchase order(s) doesn't have same currency."))

            if r.stock_picking_ids and r.purchase_order_ids:
                # check selected po, in which its pickings are not selected
                po_without_picking = r._get_selected_po_without_selected_picking()
                if po_without_picking:
                    raise ValidationError(_("The purchase order(s) `%s` does't have any selected transfer.")
                                          % (','.join(po_without_picking.mapped('name'))))
                # check selected picking, in which its po is not selected
                picking_without_po = r._get_selected_picking_without_selected_po()
                if picking_without_po:
                    raise ValidationError(_("The transfer(s) `%s` is not in selected purchase order(s).")
                                          % (','.join(picking_without_po.mapped('name'))))

    @api.depends('account_move_ids')
    def _compute_move_count(self):
        for r in self:
            r.account_moves_count = len(r.account_move_ids)

    @api.depends('partner_id')
    def _compute_payment_term_id(self):
        for r in self:
            r.payment_term_id  = r.partner_id.property_supplier_payment_term_id or r.company_id.import_tax_payment_term_id

    @api.onchange('purchase_order_ids')
    def onchange_purchase_order_ids(self):
        if not self.purchase_order_ids:
            if not self.company_id:
                self.currency_id = self.env.company.currency_id
        else:
            selecting_pickings = self.env['stock.picking']
            StockPicking = self.env['stock.picking']
            po_without_selected_picking = self.purchase_order_ids.filtered(lambda po:
                                                                           not (po.picking_ids & self.stock_picking_ids))
            for po in po_without_selected_picking:
                stock_picking = StockPicking.search([('purchase_id', 'in', po.ids),
                                                     ('state', 'in', ['assigned', 'done']),
                                                     ('custom_dec_required', '=', True)], limit=1)
                selecting_pickings |= stock_picking
            self.stock_picking_ids |= selecting_pickings

            if not self._check_po_same_partner():
                return {
                    'warning': {
                        'title': _('Purchase Order Vendor Warning!'),
                        'message': _("The selected purchase order(s) doesn't have same vendor. Please recheck it.")
                    }
                }

            if self._check_po_same_currency():
                self.currency_id = self.purchase_order_ids.currency_id
            else:
                self.currency_id = self.env.company.currency_id
                return {
                    'warning': {
                        'title': _('Purchase Order Currency Warning!'),
                        'message': _("The selected purchase order(s) doesn't have same currency. Please recheck it.")
                    }
                }

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', '/') == '/':
                vals['name'] = self.env['ir.sequence'].next_by_code('custom.declaration.import') or '/'
        res = super(CustomDeclarationImport, self).create(vals_list)
        return res

    def _prepare_custom_declaration_lines_data(self):
        lines = self.env['custom.declaration.line']
        if self.stock_picking_ids:
            # update again selected po
            adding_selected_po = self.env['purchase.order']
            for picking in self.stock_picking_ids:
                if picking.purchase_id and picking.purchase_id.id not in self.purchase_order_ids.ids:
                    adding_selected_po |= picking.purchase_id
            if adding_selected_po:
                self.purchase_order_ids |= adding_selected_po

            currency_rate = self.currency_rate
            if float_is_zero(currency_rate, precision_rounding=self.currency_id.rounding):
                if self.currency_id and self.company_id:
                    date = self.clearance_date or self.request_date or fields.Date.today()
                    currency_rate = self.currency_id._get_conversion_rate(self.currency_id, self.company_id.currency_id, self.company_id or self.env.company, date)
                else:
                    currency_rate = 1.0

            for move in self.stock_picking_ids.move_lines:
                if not move.purchase_line_id:
                    continue

                if move.product_id.valuation != 'real_time' or move.product_id.cost_method not in ['fifo', 'average']:
                    transfer_name = move.picking_id.name  # store the name before destroying the self.stock_picking_ids variable
                    self.stock_picking_ids = False
                    self.purchase_order_ids = False
                    return {'warning': {
                        'title': _('Product Costing Method Warning!'),
                        'message': _("The selected transfer '%s' does not contain any move that could be used in Custom Declaration."
                                     " Custom Declarations are only possible for products configured in automated valuation"
                                     " with FIFO or AVCO costing method. Please make sure it is the case, or you selected"
                                     " the correct transfer") % (transfer_name,)
                        }
                    }

                # set round=False to reduce difference when we have multiple picking of same PO,
                # which need to create custom declaration
                qty = move.product_uom._compute_quantity(move.product_uom_qty, move.purchase_line_id.product_uom, round=False)
                if float_is_zero(currency_rate, precision_rounding=self.currency_id.rounding):
                    total_cost_currency = sum(move.stock_valuation_layer_ids.mapped('value'))
                    total_cost = total_cost_currency

                else:
                    # Remove old source code related to landed_cost_value in stock move
                    # landed_cost = hasattr(move, 'landed_cost_value') and move.landed_cost_value or 0.0
                    # total_cost_currency = move.purchase_line_id.price_unit * qty + (landed_cost / currency_rate)
                    if move.purchase_line_id.product_qty > 0:
                        total_cost_currency = move.purchase_line_id.price_total * (qty/move.purchase_line_id.product_qty)
                        total_cost = total_cost_currency * currency_rate

                vals = move._prepare_custom_declaration_import_line_data(total_cost, total_cost_currency, qty)
                lines += lines.new(vals)
        return lines

    @api.onchange('custom_declaration_line_ids', 'compute_tax_lines_onfly')
    def _onchange_custom_declaration_line_ids(self):
        if self.compute_tax_lines_onfly:
            self._set_tax_lines()

    @api.depends('purchase_order_ids')
    def _compute_currency_id(self):
        for r in self:
            if r.purchase_order_ids and len(r.purchase_order_ids.currency_id) == 1:
                r.currency_id = r.purchase_order_ids.currency_id
            else:
                r.currency_id = r.company_id.currency_id

    @api.depends('purchase_order_ids', 'stock_picking_ids')
    def _compute_available_data_based_on_selected_order(self):
        for r in self:
            picking_domain = [('location_dest_id.is_custom_clearance', '=', True),
                              ('state', 'in', ['assigned', 'done']),
                              ('picking_type_id.code', '=', 'incoming')]
            if r.purchase_order_ids:
                invoice_domain = [('partner_id', 'in', r.purchase_order_ids.partner_id.ids), ('move_type', '=', 'in_invoice')]
                r.available_invoice_ids = self.env['account.move'].search(invoice_domain)
                picking_domain += [('group_id', 'in', r.purchase_order_ids.picking_ids.group_id.ids)]
                r.available_picking_ids = self.env['stock.picking'].search(picking_domain)
            else:
                r.available_invoice_ids = self.env['account.move'].search([('move_type', '=', 'in_invoice')])
                r.available_picking_ids = self.env['stock.picking'].search(picking_domain)

    def action_confirm(self):
        for r in self:
            for line in r.tax_line_ids:
                line.ensure_allow_reconciliation()
                account_move_line_ids = []
                if line.currency_amount_tax > 0:
                    account_move_line_ids += line._prepare_account_move_lines()

                    if account_move_line_ids:
                        vals = {
                            'journal_id': r.journal_id.id,
                            'company_id': r.env.user.company_id.id,
                            'date': r.request_date,
                            'ref': r.name,
                            'line_ids': account_move_line_ids,
                        }
                        if r.purchase_order_ids:
                            vals['custom_declaration_import_id'] = r.id

                        move = r.env['account.move'].create(vals)
                        move._post()
                        line.write({'move_id': move.id})

        super(CustomDeclarationImport, self).action_confirm()

    def _get_tax_line_model(self):
        return 'custom.declaration.tax.import'

    def _get_inconsistent_pickings(self):
        self.ensure_one()
        inconsistent_pickings = self.env['stock.picking']
        declared_stock_moves = self.stock_picking_ids.move_lines.filtered(lambda ml: ml.purchase_line_id)
        if len(self.custom_declaration_line_ids.stock_move_id) != len(declared_stock_moves):
            return self.stock_picking_ids
        # calculate product quantity of each product to compare for each line
        for dec_line in self.custom_declaration_line_ids:
            stock_move = dec_line.stock_move_id
            qty = stock_move.product_uom._compute_quantity(stock_move.product_uom_qty,
                                                           stock_move.purchase_line_id.product_uom, round=False)
            if stock_move.product_id != dec_line.product_id or float_compare(dec_line.qty, qty, 2) != 0:
                inconsistent_pickings |= stock_move.picking_id

        return inconsistent_pickings

    def _prepare_landed_cost_data(self):
        res = super(CustomDeclarationImport, self)._prepare_landed_cost_data()
        res.update({'custom_declaration_import_id': self.id})
        return res

    def _should_create_landed_cost(self):
        return True

    def _get_selected_po_without_selected_picking(self):
        self.ensure_one()
        po_without_picking = self.env['purchase.order']
        for po in self.purchase_order_ids:
            if not (po.picking_ids & self.stock_picking_ids):
                po_without_picking |= po
        return po_without_picking

    def _get_selected_picking_without_selected_po(self):
        self.ensure_one()
        picking_without_po = self.env['stock.picking']
        for picking in self.stock_picking_ids:
            if picking.purchase_id not in self.purchase_order_ids:
                picking_without_po |= picking
        return picking_without_po

    def _check_po_same_currency(self):
        self.ensure_one()
        return len(self.purchase_order_ids.currency_id) == 1

    def _check_po_same_partner(self):
        self.ensure_one()
        return len(self.purchase_order_ids.partner_id) == 1

    def _split_expense_for_dec_lines(self, expense):
        # split expense for each declaration line
        self.ensure_one()
        dec_line_dic = {}
        if expense.expense_value > 0:
            if expense.applied_product_ids:
                # calculate for declaration lines, which has product in applied products
                dec_lines = self.custom_declaration_line_ids.filtered(lambda cl: cl.product_id in expense.applied_product_ids)
            else:
                # calculate for all declaration lines
                dec_lines = self.custom_declaration_line_ids

            dec_line_dic = dec_lines._split_expense(expense)
        return dec_line_dic

    def button_split_extra_expenses(self):
        self.ensure_one()
        if self.state not in ('draft', 'open'):
                raise UserError(_("You cannot do split expenses for the declaration '%s' "
                                  "which is neither in Draft state or Open state.") % (self.name,))

        affected_dec_lines_dic = {}
        if self.extra_expense_ids._check_valid_expense():

            self.custom_declaration_line_ids.write({'extra_expense_currency': 0.0})

            for expense in self.extra_expense_ids:
                affected_dec_lines = self._split_expense_for_dec_lines(expense)
                for key, value in affected_dec_lines.items():
                    if affected_dec_lines_dic.get(key, False):
                        affected_dec_lines_dic[key] += value
                    else:
                        affected_dec_lines_dic[key] = value

            for dec_line in self.custom_declaration_line_ids:
                key = dec_line._build_key_for_declaration_line()
                if affected_dec_lines_dic.get(key, False):
                    dec_line.extra_expense_currency = affected_dec_lines_dic[key]
            # update tax lines
            if self.compute_tax_lines_onfly:
                self._set_tax_lines()
        else:
            raise ValidationError(_("Expenses are not valid, please check again."))
