from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    lock_sales_prices = fields.Boolean(related='company_id.lock_sales_prices', readonly=False)
    sales_price_modifying_group_id = fields.Many2one('res.groups', related='company_id.sales_price_modifying_group_id', readonly=False, required=True)
