from odoo import models, fields, api, _
from odoo.exceptions import UserError


class VoucherType(models.Model):
    _name = 'voucher.type'
    _description = 'Promotion Voucher type'

    name = fields.Char(string='Name', required=True)
    value = fields.Float(string='Voucher Value', required=True, help="The credit you give to vouchers of this type for future payment")
    property_promotion_voucher_profit_account_id = fields.Many2one('account.account', string='Voucher Profit Account',
                                                                   company_dependent=True,
                                                                   domain=[('deprecated', '=', False)],
                                                                   help="When customers make payment using a promotion voucher of this type, the profit created"
                                                                   " by the voucher credit will be encoded into this account. If None is set, the income account"
                                                                   " set on the voucher product will be used.")
    property_promotion_voucher_loss_account_id = fields.Many2one('account.account', string='Voucher Loss Account',
                                                                 company_dependent=True,
                                                                 domain=[('deprecated', '=', False)],
                                                                 help="When customers make payment using a promotion voucher of this type, the loss created"
                                                                 " by the voucher credit will be encoded into this account. If None is set, the expense account"
                                                                 " set on the voucher product will be used.")
    property_promotion_voucher_journal = fields.Many2one('account.journal', string='Account Journal', company_dependent=True)
    description = fields.Text(string='Description')
    payable_once = fields.Boolean(string='Payable Once', help="If checked, vouchers of this type can be used for payment only once even their credit still remains")
    valid_duration = fields.Integer(string='Valid Duration', default=30, required=True, help="Number of days before the vouchers of this type become expired"
                                    " counting from date of voucher activation")
    voucher_ids = fields.One2many('voucher.voucher', 'voucher_type_id', string='Vouchers')
    vouchers_count = fields.Integer(string='Vouchers Count', compute='_compute_vouchers_count')

    _sql_constraints = [
        ('value_positive_check',
         'CHECK(value > 0)',
         "Voucher Value must be greater than zero"),
        ('valid_duration_positive_check',
         'CHECK(valid_duration > 0)',
         "Voucher's Valid Duration must be greater than zero"),
    ]

    @api.depends('voucher_ids')
    def _compute_vouchers_count(self):
        for r in self:
            r.vouchers_count = len(r.voucher_ids)

    def write(self, vals):
        if 'value' in vals:
            for r in self.mapped('voucher_ids'):
                raise UserError(_("You may not change the Voucher Value of the voucher type '%s' when there is a voucher refers to it."
                                  " Please either delete all corresponding vouchers of this type or create new voucher type.") % (r.name,))
        return super(VoucherType, self).write(vals)

    def unlink(self):
        if self.voucher_ids:
            raise UserError(_('Could not delete a voucher type associated vouchers'))
        return super(VoucherType, self).unlink()
