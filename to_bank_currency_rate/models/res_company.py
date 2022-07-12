from odoo import models, fields


class ResCompany(models.Model):
    _inherit = "res.company"

    main_currency_bank_id = fields.Many2one('res.bank', string='Main Bank',
                                            help="The bank whose exchange rates are used for currency conversion when no"
                                            " specific bank is known. Leave this empty to disable this function to apply"
                                            " the latest rate to the transaction date no matter the bank is specified or not.")

