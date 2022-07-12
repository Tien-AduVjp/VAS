# -*- coding: utf-8 -*-
from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    currency_conversion_diff_journal_id = fields.Many2one(
        'account.journal',
        related='company_id.currency_conversion_diff_journal_id', readonly=False,
        string="Currency Conversion Difference Journal",
        domain="[('company_id', '=', company_id), ('type', '=', 'general')]",
        help='The accounting journal where automatic currency conversion differences will be registered')
