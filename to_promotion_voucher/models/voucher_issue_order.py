from odoo import api, fields, models, _
from odoo.exceptions import UserError


class VoucherIssueOrder(models.Model):
    _name = 'voucher.issue.order'
    _description = 'Voucher Issue Order'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'planned_date asc,id'

    @api.model
    def _get_default_picking_type(self):
        return self.env['stock.picking.type'].search([
            ('code', '=', 'voucher_issue_order'),
            ('company_id', '=', self.env.context.get('company_id', self.env.company.id)),
            '|',
            ('warehouse_id.company_id', '=', self.env.context.get('company_id', self.env.company.id)),
            ('warehouse_id', '=', False)], limit=1)

    name = fields.Char(
        'Reference', copy=False, readonly=True, default='/')
    origin = fields.Char(
        'Source', copy=False,
        help="Reference of the document that generated this order request.")

    product_id = fields.Many2one(
        'product.product', 'Voucher Product',
        domain=[('is_promotion_voucher', '=', True)],
        readonly=False, required=True,
        states={'confirmed': [('readonly', True)],
                'done': [('readonly', True)],
                'cancel': [('readonly', True)]})
    product_tmpl_id = fields.Many2one('product.template', 'Product Template', related='product_id.product_tmpl_id')
    voucher_qty = fields.Integer(
        'Quantity', default=1, readonly=False, required=True,
        states={'confirmed': [('readonly', True)],
                'done': [('readonly', True)],
                'cancel': [('readonly', True)]})
    uom_category_id = fields.Many2one(related='product_id.uom_id.category_id')
    product_uom_id = fields.Many2one(
        'uom.uom', 'Product Unit of Measure', readonly=False, required=True,
        states={'confirmed': [('readonly', True)],
                'done': [('readonly', True)],
                'cancel': [('readonly', True)]},
        domain="[('category_id', '=', uom_category_id)]")
    picking_type_id = fields.Many2one(
        'stock.picking.type', 'Picking Type', domain=[('code', '=', 'voucher_issue_order')],
        default=_get_default_picking_type, required=True, readonly=False, states={'confirmed': [('readonly', True)],
                                                                                  'done': [('readonly', True)],
                                                                                  'cancel': [('readonly', True)]})
    planned_date = fields.Datetime(
        'Planned Date', copy=False, default=fields.Datetime.now, readonly=False,
        index=True, states={'confirmed': [('readonly', True)],
                            'done': [('readonly', True)],
                            'cancel': [('readonly', True)]})
    valid_duration = fields.Integer(string='Valid Duration', required=True, index=True, readonly=False,
                                    help='Number of days before the vouchers become expired counting from date of voucher activated',
                                    states={'confirmed': [('readonly', True)],
                                            'done': [('readonly', True)],
                                            'cancel': [('readonly', True)]})
    issued_date = fields.Date(string='Issued Date', index=True, readonly=False, states={'confirmed': [('readonly', True)],
                                                                                        'done': [('readonly', True)],
                                                                                        'cancel': [('readonly', True)]})
    move_finished_ids = fields.One2many(
        'stock.move', 'order_id', 'Finished Move',
        copy=False, readonly=True)

    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('done', 'Done'),
        ('cancel', 'Cancelled')], string='State',
        copy=False, default='draft', tracking=True)

    user_id = fields.Many2one('res.users', 'Responsible', default=lambda self: self._uid)
    company_id = fields.Many2one(
        'res.company', 'Company',
        default=lambda self: self.env.company,
        required=True)

    _sql_constraints = [
        ('qty_positive', 'check (voucher_qty > 0)', 'The quantity to issue must be positive!'),
        ('valid_duration_check', 'check (valid_duration > 0)', 'The valid duration must be greater than zero!'),
    ]

    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            self.product_uom_id = self.product_id.uom_id.id
            self.valid_duration = self.product_id.voucher_type_id.valid_duration

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', '/') == '/':
                vals['name'] = self.env['ir.sequence'].next_by_code('voucher.issue.order') or '/'
        return super(VoucherIssueOrder, self).create(vals_list)

    def unlink(self):
        if any(order.state not in ('cancel', 'draft') for order in self):
            raise UserError(_('Could not delete a voucher issue order not in draft or cancel state'))
        return super(VoucherIssueOrder, self).unlink()

    def action_confirm(self):
        for r in self:
            r.write({'state': 'confirmed'})

    def action_draft(self):
        for r in self:
            r.write({'state': 'draft'})

    def action_cancel(self):
        for r in self:
            r.write({'state': 'cancel'})

    def action_issue(self):
        self._generate_moves()
        self.write({
            'state': 'done',
            'issued_date': fields.Date.today()
            })

    def _generate_moves(self):
        moves = self.env['stock.move']
        for r in self:
            if not r.picking_type_id.default_location_src_id or not r.picking_type_id.default_location_dest_id:
                raise UserError(_("You need to set up a Default Source Location and a Default Destination Location for the Operations Types '%s'")
                                % r.picking_type_id.name)
            move = self.env['stock.move'].create({
                'name': r.name,
                'date': fields.Datetime.now(),
                'product_id': r.product_id.id,
                'product_uom': r.product_id.uom_id.id,
                'product_uom_qty': r.voucher_qty,
                'location_id': r.picking_type_id.default_location_src_id.id,
                'location_dest_id': r.picking_type_id.default_location_dest_id.id,
                'company_id': self.env.company.id,
                'origin': r.name,
                'order_id': r.id,
                'picking_type_id': r.picking_type_id.id
            })
            move._action_confirm()
            move.validate_promotion_voucher_move(lot_ids=False)
            move._action_done()
            moves |= move
        return moves
