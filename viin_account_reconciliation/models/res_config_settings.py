# -*- coding: utf-8 -*-

from odoo import models, fields


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    account_bank_reconciliation_start = fields.Date(string="Bank Reconciliation Threshold",
        related='company_id.account_bank_reconciliation_start', readonly=False,
        help="""The bank reconciliation widget won't ask to reconcile payments older than this date.
               This is useful if you install accounting after having used invoicing for some time and
               don't want to reconcile all the past payments with bank statements.""")
