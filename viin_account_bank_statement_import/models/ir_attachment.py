# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    @api.model
    def _validate_bank_statement_line_vals(self, vals):
        if not vals.get('payment_ref', ''):
            raise UserError(_("No payment reference specified in file content."))
        vals.update({
            'date': fields.Date.to_date(vals.get('date', fields.Date.today())),
            'amount': float(vals.get('amount', 0.0))
            })
        return vals

    def _parse_as_bank_statement(self):
        """ Each module adding a file support must extends this method. It processes the file if it can, returns super otherwise, resulting in a chain of responsibility.
            This method parses the given file and returns the data required by the bank statement import process, as specified below.
            rtype: triplet (if a value can't be retrieved, use None)
                - currency code: string (e.g: 'EUR')
                    The ISO 4217 currency code, case insensitive
                - account number: string (e.g: 'BE1234567890')
                    The number of the bank account which the statement belongs to
                - bank statements data: list of dict containing (optional items marked by o) :
                    - 'name': string (e.g: '000000123')
                    - 'date': date (e.g: 2013-06-26)
                    -o 'balance_start': float (e.g: 8368.56)
                    -o 'balance_end_real': float (e.g: 8888.88)
                    - 'transactions': list of dict containing :
                        - 'payment_ref': string (e.g: 'KBC-INVESTERINGSKREDIET 787-5562831-01')
                        - 'date': date
                        - 'amount': float
                        - 'unique_import_id': string
                        -o 'account_number': string
                            Will be used to find/create the res.partner.bank in odoo
                        -o 'note': string
                        -o 'partner_name': string
                        -o 'ref': string
        """
        raise UserError(_("Could not make sense of the given file '%s' which is in `%s` format that is not supported yet.")
                          % (self.display_name, self.mimetype))
