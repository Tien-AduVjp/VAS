from odoo import models, fields


class PromotionVoucherConfiguration(models.TransientModel):
    _inherit = 'res.config.settings'

    property_promotion_voucher_profit_account_id = fields.Many2one(related='company_id.property_promotion_voucher_profit_account_id',
                                                                   domain=[('deprecated', '=', False)], readonly=False)
    property_promotion_voucher_loss_account_id = fields.Many2one(related='company_id.property_promotion_voucher_loss_account_id',
                                                                 domain=[('deprecated', '=', False)], readonly=False)
    property_unearn_revenue_account_id = fields.Many2one(related='company_id.property_unearn_revenue_account_id',
                                                         domain=[('deprecated', '=', False)], readonly=False)
