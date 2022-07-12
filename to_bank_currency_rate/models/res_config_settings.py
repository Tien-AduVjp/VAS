from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    main_currency_bank_id = fields.Many2one('res.bank', related='company_id.main_currency_bank_id', readonly=False)
