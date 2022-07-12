import random
import logging

from datetime import timedelta
from string import digits

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError

_logger = logging.getLogger(__name__)


class VoucherVoucher(models.Model):
    _name = 'voucher.voucher'
    _description = 'Promotion Voucher'
    _inherit = ['mail.thread', 'mail.activity.mixin', 'to.base']

    name = fields.Char(string='Name', compute='_compute_name', store=True)
    lot_id = fields.Many2one('stock.production.lot', index=True,
                             string="Logistics Serial Number", help='The unique logistics serial number that associated with the Equipment')
    product_id = fields.Many2one('product.product', string='Associated Product', related='lot_id.product_id', store=True, index=True, readonly=True)
    voucher_type_id = fields.Many2one(related='product_id.product_tmpl_id.voucher_type_id', store=True, index=True)
    current_stock_location_id = fields.Many2one('stock.location', string='Current Stock Location', tracking=True,
                                                compute='_compute_current_stock_location', store=True, index=True)
    value = fields.Float(string='Voucher Value', related='product_id.product_tmpl_id.value', store=True, readonly=True)

    price = fields.Float(string='Sold Price', readonly=True,
                         help="The actual price when selling this promotion voucher")
    used_amount = fields.Float(string='Used Amount', default=0.0, readonly=True)
    serial = fields.Char(string='Serial of Voucher', readonly=True)
    activated_date = fields.Date(string='Activated Date', readonly=True, tracking=True)
    issue_date = fields.Date(string='Issued Date', readonly=True)
    expiry_date = fields.Date(string='Expiry Date', readonly=True, compute='_compute_expiry_date', store=True, tracking=True)
    state = fields.Selection([
        ('new', 'New'),
        ('activated', 'Activated'),
        ('expired', 'Expired'),
        ('used', 'Used')], string='Status', default='new', readonly=True, required=True, tracking=True)
    stock_move_lines = fields.One2many('stock.move.line', 'voucher_id', string='Move History')
    history_count = fields.Integer(string='Move Lines Count', compute='_compute_history_count')
    issue_order_id = fields.Many2one('voucher.issue.order', string='Issue Order', index=True)
    valid_duration = fields.Integer(string='Valid Duration', index=True, readonly=True, related='issue_order_id.valid_duration', store=True, tracking=True,
                                    help='Number of days before the vouchers become expired counting from date of voucher activated')
    used_date = fields.Datetime(string='Used Date')
    used_before = fields.Boolean(help="Technical field for knowing if voucher has been used before", copy=False)

    _sql_constraints = [
        ('unique_serial', 'unique(serial)', 'The serial has been declared.'),
        ('unique_lot_id', 'unique(lot_id)', 'The logistics lot must be unique.'),
        ('check_over_use', 'CHECK(used_amount <= value)', 'The Used Amount must be less than or equal to the Voucher Value.')
    ]

    @api.depends('product_id', 'lot_id')
    def _compute_name(self):
        for r in self:
            if r.product_id and r.lot_id:
                r.name = r.product_id.name + '/' + r.lot_id.name
            else:
                r.name = '/'

    @api.depends('lot_id', 'lot_id.quant_ids')
    def _compute_current_stock_location(self):
        for r in self:
            if r.lot_id:
                quants = r.lot_id.quant_ids.filtered(lambda x: x.quantity > 0).sorted(lambda x: x.in_date, reverse=True)
                if quants:
                    r.current_stock_location_id = quants[0].location_id
            else:
                r.current_stock_location_id = False

    def _compute_history_count(self):
        data = self.env['stock.move.line'].sudo().read_group([('voucher_id', 'in', self.ids)], ['voucher_id'], ['voucher_id'])
        mapped_data = dict([(dict_data['voucher_id'][0], dict_data['voucher_id_count']) for dict_data in data])
        for r in self:
            r.history_count = mapped_data.get(r.id, 0)

    @api.depends('activated_date', 'valid_duration')
    def _compute_expiry_date(self):
        for r in self:
            if r.activated_date and r.valid_duration:
                r.expiry_date = r.activated_date + timedelta(days=r.valid_duration)

    def spend(self, amount):
        self.ensure_one()
        data = {'used_amount': self.used_amount + amount}
        if self.state == 'new':
            raise ValidationError(_("The voucher '%s [%s]' must be activated prior to being available as a payment mean") % (self.name, self.serial))
        elif self.state == 'activated':
            data['state'] = 'used'
            data['used_before'] = True
        elif self.state == 'used':
            if self.product_id.payable_once:
                raise ValidationError(_("The voucher %s [%s] allow one-time usage only. It was once used already...") % (self.name, self.serial))
        self.write(data)

    def unspend(self, amount):
        self.ensure_one()
        if self.used_amount:
            if amount > self.used_amount:
                raise ValidationError(_("The amount to be deducted is exceeding the amount used of voucher %s [%s]") % (self.name, self.serial))
            if self.state != 'used':
                raise ValidationError(_("The voucher '%s [%s]' must be used") % (self.name, self.serial))
            self.write({
                'used_amount': self.used_amount - amount,
                'state': 'activated'
            })

    def _prepare_expired_voucher_move_lines_data(self):
        move_lines = []
        product_accounts = self.product_id.product_tmpl_id._get_product_accounts()
        # credit line
        move_lines.append((0, 0, {
            'name': self.product_id.name,
            'ref': self.serial,
            'account_id': product_accounts['voucher_profit'] and product_accounts['voucher_profit'].id or False,
            'credit': self.price  # Sold price
            }))
        # debit line
        move_lines.append((0, 0, {
            'name': self.product_id.name,
            'ref': self.serial,
            'account_id': product_accounts['income'] and product_accounts['income'].id or False,
            'debit': self.price  # Sold price
            }))
        return move_lines

    def _prepare_expired_voucher_move_data(self):
        ref = 'VOUCHER/EXPIRED-VOUCHER/' + str(fields.Date.today())
        journal_id = self.env['account.journal'].search([('code', '=', 'PVJ')], limit=1)
        if not journal_id:
            return False

        move_lines_data = []
        for r in self:
            move_lines_data += r._prepare_expired_voucher_move_lines_data()
        data = {
            'journal_id': journal_id.id,
            'date': fields.date.today(),
            'ref': ref,
            'line_ids': move_lines_data
        }
        return data

    def action_set_expiry(self):
        if self._context.get('ignore_check_set_expire_voucher_right', False) and not self.env.user.has_group('to_promotion_voucher.group_promotion_voucher_manager'):
            raise UserError(_("Only user in the group %s can manually set a voucher to expired status.")
                            % self.env.ref('to_promotion_voucher.group_promotion_voucher_manager').display_name)
        for r in self:
            if r.state == 'expired':
                raise UserError(_("The voucher %s is expired already.") % r.name)
        to_create_move_voucher = self.filtered(lambda x: x.price > 0.0)
        if to_create_move_voucher:
            move_vals = to_create_move_voucher._prepare_expired_voucher_move_data()
            move = self.env['account.move'].create(move_vals)
            move.post()
        valid_duration = 0
        if self.activated_date:
            valid_duration = (fields.Date.today() - self.activated_date).days
        self.write({'state': 'expired', 'expiry_date': fields.Date.today(), 'valid_duration': valid_duration})

    @api.model
    def cron_check_expired_and_create_entries(self):
        expired_vouchers = self.env['voucher.voucher'].search([
            ('expiry_date', '<', fields.Date.today()),
            ('state', '!=', 'expired')
            ])
        if expired_vouchers:
            expired_vouchers.with_context(ignore_check_set_expire_voucher_right=True).action_set_expiry()

    def _generate_serial(self):
        barcode = None
        while not barcode or self.barcode_exists(barcode=barcode, barcode_field='serial', inactive_rec=False):
            ran_str = "".join(random.choice(digits) for x in range(12))
            barcode = self.get_ean13(ran_str)
        return barcode

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            vals['serial'] = vals.get('serial', self._generate_serial())
        return super(VoucherVoucher, self).create(vals_list)
