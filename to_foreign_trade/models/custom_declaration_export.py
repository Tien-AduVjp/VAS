from odoo import models, api, fields, _
from odoo.exceptions import ValidationError
from odoo.tools import float_is_zero, float_compare

class CustomDeclarationExport(models.Model):
    _name = 'custom.declaration.export'
    _description = 'Export Custom Declaration'
    _inherit = ['abstract.custom.declaration', 'mail.thread', 'mail.activity.mixin']

    sale_order_id = fields.Many2one('sale.order', string="Sales Order", domain=[('state', 'in', ['sale', 'done']), ('foreign_trade', '=', True)],
                                    readonly=False, states={'open': [('readonly', True)],
                                                            'confirm': [('readonly', True)],
                                                            'done': [('readonly', True)],
                                                            'cancel': [('readonly', True)]})

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

    @api.constrains('sale_order_id', 'stock_picking_id')
    def _check_so_vs_picking(self):
        for r in self:
            if r.stock_picking_id and r.sale_order_id and r.stock_picking_id.sale_id.id != r.sale_order_id.id:
                raise ValidationError(_("The transfer '%s' and the sale order '%s' are not relevant.") 
                                      % (r.sale_order_id.display_name, r.stock_picking_id.display_name))

    @api.depends('account_move_ids')
    def _compute_move_count(self):
        for r in self:
            r.account_moves_count = len(r.account_move_ids)
    
    @api.depends('partner_id')
    def _compute_payment_term_id(self):
        for r in self:
            r.payment_term_id = r.partner_id.property_payment_term_id or r.company_id.export_tax_payment_term
            
    @api.onchange('sale_order_id')
    def onchange_sale_order_id(self):
        if not self.sale_order_id:
            self.currency_id = self.env.company.currency_id
        else:
            StockPicking = self.env['stock.picking']
            stock_picking = StockPicking.search([('sale_id', '=', self.sale_order_id.id), ('custom_dec_required', '=', True)], limit=1)
            self.stock_picking_id = stock_picking
            self.currency_id = self.sale_order_id.currency_id

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', '/') == '/':
                vals['name'] = self.env['ir.sequence'].next_by_code('custom.declaration.export') or '/'
        return super(CustomDeclarationExport, self).create(vals_list)

    def _prepare_custom_declaration_lines_data(self):
        lines = self.env['custom.declaration.line']
        if self.stock_picking_id:
            if not self.sale_order_id:
                if self.stock_picking_id.sale_id:
                    self.sale_order_id = self.stock_picking_id.sale_id
                    
            currency_rate = self.currency_rate
            if float_is_zero(currency_rate, precision_rounding=self.currency_id.rounding):
                if self.currency_id and self.company_id:
                    date = self.clearance_date or self.request_date or fields.Date.today()
                    currency_rate = self.currency_id._get_conversion_rate(self.currency_id, self.company_id.currency_id, self.company_id or self.env.company, date)
                else:
                    currency_rate = 1.0
                    
            for move in self.stock_picking_id.move_lines:
                if move.product_id.valuation != 'real_time' or move.product_id.cost_method not in ['fifo', 'average']:
                    transfer_name = self.stock_picking_id.name  # store the name before destroying the self.stock_picking_id variable
                    self.stock_picking_id = False
                    self.sale_order_id = False
                    return {'warning': {
                        'title': _('Product Costing Method Warning!'),
                        'message': _("The selected transfer '%s' does not contain any move that could be used in Custom Declaration."
                                     " Custom Declarations are only possible for products configured in automated valuation"
                                     " with FIFO or AVCO costing method. Please make sure it is the case, or you selected"
                                     " the correct transfer") % (transfer_name,)
                        }
                    }
                
                sale_line_id = move.move_dest_ids.sale_line_id
                if sale_line_id and sale_line_id.order_id == self.sale_order_id and sale_line_id.product_uom_qty > 0:
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

    @api.depends('sale_order_id')
    def _compute_currency_id(self):
        for r in self:
            if r.sale_order_id:
                r.currency_id = r.sale_order_id.currency_id
            else:
                r.currency_id = r.company_id.currency_id
    
    @api.depends('sale_order_id', 'stock_picking_id')
    def _compute_available_data_based_on_selected_order(self):
        for r in self:
            picking_domain = [('location_dest_id.is_custom_clearance', '=', True), 
                              ('state', 'in', ['assigned', 'done']),
                              ('picking_type_id.code', '=', 'internal')]
            if r.sale_order_id:
                invoice_domain = [('partner_id', '=', r.sale_order_id.partner_id.id), ('type', '=', 'out_invoice')]
                r.available_invoice_ids = self.env['account.move'].search(invoice_domain)
                if r.stock_picking_id:
                    picking_domain += [('group_id', '=', r.stock_picking_id.group_id.id)]
                    r.available_picking_ids = self.env['stock.picking'].search(picking_domain)
                else:
                    r.available_picking_ids = self.env['stock.picking'].search(picking_domain)
            else:
                r.available_invoice_ids = self.env['account.move'].search([('type', '=', 'out_invoice')])
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
                            'company_id': r.env.company.id,
                            'date': r.request_date,
                            'ref': r.name,
                            'line_ids': account_move_line_ids,
                        }
                        if r.sale_order_id:
                            vals['custom_declaration_export_id'] = r.id
                        move = r.env['account.move'].create(vals)
                        move.post()
                        line.write({'move_id': move.id})

        super(CustomDeclarationExport, self).action_confirm()

    def _get_tax_line_model(self):
        return 'custom.declaration.tax.export'

    def _check_picking_and_declaration_lines_consistency(self):
        self.ensure_one()
        if len(self.custom_declaration_line_ids) != len(self.stock_picking_id.move_lines):
            return False
        # calculate product quantity of each product to compare
        dec_lines_dic = {}
        mov_lines_dic = {}
        for dec_line in self.custom_declaration_line_ids:
            if not dec_lines_dic.get(dec_line.product_id.id, False):
                dec_lines_dic[dec_line.product_id.id] = dec_line.qty
            else:
                dec_lines_dic[dec_line.product_id.id] += dec_line.qty
        
        for mov_line in self.stock_picking_id.move_lines:
            sale_line_id = mov_line.move_dest_ids.sale_line_id
            qty = mov_line.product_uom._compute_quantity(mov_line.product_uom_qty, sale_line_id.product_uom, round=False)
            if not mov_lines_dic.get(mov_line.product_id.id, False):
                mov_lines_dic[mov_line.product_id.id] = qty
            else:
                mov_lines_dic[mov_line.product_id.id] += qty
        
        for product, qty  in dec_lines_dic.items():
            if not mov_lines_dic.get(product, False) or float_compare(mov_lines_dic[product], qty, 2) != 0:
                return False
        
        return True
