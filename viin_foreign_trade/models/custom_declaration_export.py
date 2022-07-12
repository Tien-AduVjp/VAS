from odoo import models, api, fields, _
from odoo.exceptions import ValidationError
from odoo.tools import float_is_zero, float_compare

class CustomDeclarationExport(models.Model):
    _name = 'custom.declaration.export'
    _description = 'Export Custom Declaration'
    _inherit = ['abstract.custom.declaration', 'mail.thread', 'mail.activity.mixin']

    sale_order_ids = fields.Many2many('sale.order', string="Sales Order", domain=[('state', 'in', ['sale', 'done']), ('foreign_trade', '=', True)],
                                    readonly=True, states={'draft': [('readonly', False)]})

    custom_declaration_line_ids = fields.One2many('custom.declaration.line', 'custom_declaration_export_id', string="Request Line", readonly=False,
                               states={'confirm': [('readonly', True)],
                                       'done': [('readonly', True)],
                                       'cancel': [('readonly', True)]})

    tax_line_ids = fields.One2many('custom.declaration.tax.export', 'custom_declaration_id', string="Tax Lines", readonly=False,
                               states={'confirm': [('readonly', True)],
                                       'done': [('readonly', True)],
                                       'cancel': [('readonly', True)]})

    custom_dec_tax_group_ids = fields.One2many('custom.declaration.tax.export.group', 'custom_declaration_id', string='Tax Groups', readonly=True)

    account_move_ids = fields.One2many('account.move', 'custom_declaration_export_id', string="Journal Entries", readonly=True)
    account_moves_count = fields.Integer(string="# of moves", compute='_compute_move_count')
    payment_term_id = fields.Many2one('account.payment.term', string="Tax Payment Term",
                                      compute='_compute_payment_term_id', readonly=False, store=True,
                                      states={'open': [('readonly', True)],
                                              'confirm': [('readonly', True)],
                                              'done': [('readonly', True)],
                                              'cancel': [('readonly', True)]})
    landed_cost_ids = fields.One2many('stock.landed.cost', 'custom_declaration_export_id', string='Landed Cost')
    landed_cost_count = fields.Integer(string='landed Cost Count', compute='_compute_landed_cost_count', compute_sudo=True)

    @api.depends('landed_cost_ids')
    def _compute_landed_cost_count(self):
        for r in self:
            r.landed_cost_count = len(r.landed_cost_ids)

    @api.constrains('sale_order_ids', 'stock_picking_ids')
    def _check_so_vs_picking(self):
        for r in self:
            # check so, which doesn't have same partner
            if not r._check_so_same_partner():
                raise ValidationError(_("The selected sale order(s) doesn't have same customer."))

            # check so, which doesn't have same currency
            if not r._check_so_same_currency():
                raise ValidationError(_("The selected sale order(s) doesn't have same currency."))

            if r.stock_picking_ids and r.sale_order_ids:
                # check selected so, in which its pickings are not selected
                so_without_picking = r._get_selected_so_without_selected_picking()
                if so_without_picking:
                    raise ValidationError(_("The sale order(s) `%s` does't have any selected transfer.")
                                          % (','.join(so_without_picking.mapped('name'))))
                # check selected picking, in which its so is not selected
                picking_without_so = r._get_selected_picking_without_selected_so()
                if picking_without_so:
                    raise ValidationError(_("The transfer(s) `%s` is not in selected sale order(s).")
                                          % (','.join(picking_without_so.mapped('name'))))

    @api.depends('account_move_ids')
    def _compute_move_count(self):
        for r in self:
            r.account_moves_count = len(r.account_move_ids)

    @api.depends('partner_id')
    def _compute_payment_term_id(self):
        for r in self:
            r.payment_term_id = r.partner_id.property_payment_term_id or r.company_id.export_tax_payment_term_id

    @api.onchange('sale_order_ids')
    def onchange_sale_order_ids(self):
        if not self.sale_order_ids:
            if not self.company_id:
                self.currency_id = self.env.company.currency_id
        else:
            selecting_pickings = self.env['stock.picking']
            StockPicking = self.env['stock.picking']
            so_without_selected_picking = self.sale_order_ids.filtered(lambda so:
                                                                       not (so.picking_ids & self.stock_picking_ids))
            for so in so_without_selected_picking:
                stock_picking = StockPicking.search([('sale_id', 'in', so.ids),
                                                     ('state', 'in', ['assigned', 'done']),
                                                     ('custom_dec_required', '=', True)], limit=1)
                selecting_pickings |= stock_picking
            self.stock_picking_ids |= selecting_pickings

            if not self._check_so_same_partner():
                return {
                    'warning': {
                        'title': _('Sale Order Customer Warning!'),
                        'message': _("The selected sale order(s) doesn't have same customer. Please recheck it.")
                    }
                }

            if self._check_so_same_currency():
                self.currency_id = self.sale_order_ids.currency_id
            else:
                self.currency_id = self.env.company.currency_id
                return {
                    'warning': {
                        'title': _('Sale Order Currency Warning!'),
                        'message': _("The selected sale order(s) doesn't have same currency. Please recheck it.")
                    }
                }

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', '/') == '/':
                vals['name'] = self.env['ir.sequence'].next_by_code('custom.declaration.export') or '/'
        return super(CustomDeclarationExport, self).create(vals_list)

    def _prepare_custom_declaration_lines_data(self):
        lines = self.env['custom.declaration.line']
        if self.stock_picking_ids:
            # update again selected so
            adding_selected_so = self.env['sale.order']
            for picking in self.stock_picking_ids:
                if picking.sale_id and picking.sale_id.id not in self.sale_order_ids.ids:
                    adding_selected_so |= picking.sale_id
            if adding_selected_so:
                self.sale_order_ids |= adding_selected_so

            currency_rate = self.currency_rate
            if float_is_zero(currency_rate, precision_rounding=self.currency_id.rounding):
                if self.currency_id and self.company_id:
                    date = self.clearance_date or self.request_date or fields.Date.today()
                    currency_rate = self.currency_id._get_conversion_rate(self.currency_id, self.company_id.currency_id, self.company_id or self.env.company, date)
                else:
                    currency_rate = 1.0

            for move in self.stock_picking_ids.move_lines:
                if move.product_id.valuation != 'real_time' or move.product_id.cost_method not in ['fifo', 'average']:
                    transfer_name = move.picking_id.name  # store the name before destroying the self.stock_picking_ids variable
                    self.stock_picking_ids = False
                    self.sale_order_ids = False
                    return {'warning': {
                        'title': _('Product Costing Method Warning!'),
                        'message': _("The selected transfer '%s' does not contain any move that could be used in Custom Declaration."
                                     " Custom Declarations are only possible for products configured in automated valuation"
                                     " with FIFO or AVCO costing method. Please make sure it is the case, or you selected"
                                     " the correct transfer") % (transfer_name,)
                        }
                    }

                sale_line_id = move.move_dest_ids.sale_line_id
                if sale_line_id and sale_line_id.order_id.id in self.sale_order_ids.ids and sale_line_id.product_uom_qty > 0:
                    # set round=False to reduce difference when we have multiple picking of same PO,
                    # which need to create custom declaration
                    qty = move.product_uom._compute_quantity(move.product_uom_qty, sale_line_id.product_uom, round=False)

                    total_cost_currency = sale_line_id.price_total * (qty/sale_line_id.product_uom_qty)
                    total_cost = total_cost_currency * currency_rate
                    vals = move._prepare_custom_declaration_export_line_data(total_cost, total_cost_currency, qty, sale_line_id)
                    lines += lines.new(vals)
        return lines

    @api.onchange('custom_declaration_line_ids', 'compute_tax_lines_onfly')
    def _onchange_custom_declaration_line_ids(self):
        if self.compute_tax_lines_onfly:
            self._set_tax_lines()

    @api.depends('sale_order_ids')
    def _compute_currency_id(self):
        for r in self:
            if r.sale_order_ids and len(r.sale_order_ids.currency_id) == 1:
                r.currency_id = r.sale_order_ids.currency_id
            else:
                r.currency_id = r.company_id.currency_id

    @api.depends('sale_order_ids', 'stock_picking_ids')
    def _compute_available_data_based_on_selected_order(self):
        for r in self:
            picking_domain = [('location_dest_id.is_custom_clearance', '=', True),
                              ('state', 'in', ['assigned', 'done']),
                              ('picking_type_id.code', '=', 'internal')]
            if r.sale_order_ids:
                invoice_domain = [('partner_id', 'in', r.sale_order_ids.partner_id.ids), ('move_type', '=', 'out_invoice')]
                r.available_invoice_ids = self.env['account.move'].search(invoice_domain)
                picking_domain += [('group_id', 'in', r.sale_order_ids.picking_ids.group_id.ids)]
                r.available_picking_ids = self.env['stock.picking'].search(picking_domain)
            else:
                r.available_invoice_ids = self.env['account.move'].search([('move_type', '=', 'out_invoice')])
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
                        if r.sale_order_ids:
                            vals['custom_declaration_export_id'] = r.id
                        move = r.env['account.move'].create(vals)
                        move._post()
                        line.write({'move_id': move.id})

        super(CustomDeclarationExport, self).action_confirm()

    def _get_tax_line_model(self):
        return 'custom.declaration.tax.export'

    def _get_inconsistent_pickings(self):
        self.ensure_one()
        inconsistent_pickings = self.env['stock.picking']
        declared_stock_moves = self.stock_picking_ids.move_lines.filtered(lambda ml: ml.move_dest_ids.sale_line_id)
        if len(self.custom_declaration_line_ids.stock_move_id) != len(declared_stock_moves):
            return self.stock_picking_ids
        # calculate product quantity of each product to compare for each line
        for dec_line in self.custom_declaration_line_ids:
            stock_move = dec_line.stock_move_id
            sale_line = dec_line.sale_order_line_id
            qty = stock_move.product_uom._compute_quantity(stock_move.product_uom_qty, sale_line.product_uom, round=False)

            if stock_move.product_id != dec_line.product_id or float_compare(dec_line.qty, qty, 2) != 0:
                inconsistent_pickings |= stock_move.picking_id

        return inconsistent_pickings

    def _prepare_landed_cost_data(self):
        res = super(CustomDeclarationExport, self)._prepare_landed_cost_data()
        res.update({'custom_declaration_export_id': self.id})
        return res

    def _get_selected_so_without_selected_picking(self):
        self.ensure_one()
        so_without_picking = self.env['sale.order']
        for so in self.sale_order_ids:
            if not (so.picking_ids & self.stock_picking_ids):
                so_without_picking |= so
        return so_without_picking

    def _get_selected_picking_without_selected_so(self):
        self.ensure_one()
        picking_without_so = self.env['stock.picking']
        for picking in self.stock_picking_ids:
            if picking.sale_id not in self.sale_order_ids:
                picking_without_so |= picking
        return picking_without_so

    def _check_so_same_currency(self):
        self.ensure_one()
        return len(self.sale_order_ids.currency_id) == 1

    def _check_so_same_partner(self):
        self.ensure_one()
        return len(self.sale_order_ids.partner_id) == 1
