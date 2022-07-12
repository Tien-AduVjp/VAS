from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'


    sales_price_modifying_group_id = fields.Many2one('res.groups', related='company_id.sales_price_modifying_group_id', readonly=False, required=True)