from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    is_promotion_voucher = fields.Boolean(string='Is Promotion Voucher')
    voucher_type_id = fields.Many2one('voucher.type', string='Voucher Type')
    value = fields.Float(string='Voucher Value', related='voucher_type_id.value', store=True)
    payable_once=fields.Boolean(related='voucher_type_id.payable_once')

    def _get_product_accounts(self):
        res = super(ProductTemplate, self)._get_product_accounts()
        res.update({
            'voucher_profit': self.voucher_type_id.property_promotion_voucher_profit_account_id or res['income'],
            'voucher_loss': self.voucher_type_id.property_promotion_voucher_loss_account_id or res['expense'],
            })
        return res

    def get_product_accounts(self, fiscal_pos=None):
        accounts = super(ProductTemplate, self).get_product_accounts(fiscal_pos)
        accounts.update({'voucher_promotion_journal': self.voucher_type_id.property_promotion_voucher_journal or False})
        return accounts

    @api.onchange('is_promotion_voucher')
    def _onchange_is_promotion_voucher(self):
        if self.is_promotion_voucher:
            self.update({
                'tracking': 'serial',
                'type': 'product',
                'categ_id': self.env.ref('to_promotion_voucher.product_category_promotion_voucher')
                })

    @api.constrains('type', 'is_promotion_voucher')
    def _constrains_product_type(self):
        for r in self.filtered(lambda r: r.is_promotion_voucher):
            if r.type != 'product':
                raise ValidationError(_("The type of a promotion voucher product '%s' must be Stockable Product.") % r.name)

    @api.constrains('is_promotion_voucher', 'tracking')
    def _constrains_tracking(self):
        for r in self.filtered(lambda r: r.is_promotion_voucher):
            if r.tracking != 'serial':
                raise ValidationError(_("The tracking method of promotion voucher '%s' must be By Unique Serial Number.") % r.name)
