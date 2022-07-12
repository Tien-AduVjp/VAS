# -*- coding: utf-8 -*-

import base64
import io
import logging

from odoo import models, fields, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

try:
    import csv
except ImportError:
    _logger.debug('Cannot `import csv`.')


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    def _check_csv(self):
        self.ensure_one()
        return self.mimetype == 'text/csv'

    def _parse_as_bank_statement(self):
        self.ensure_one()
        if not self._check_csv():
            return super(IrAttachment, self)._parse_as_bank_statement()
        statement_vals = {}
        transaction_list = []
        keys = ['date', 'payment_ref', 'partner_name', 'ref', 'narration', 'amount', 'account_number']
        try:
            csv_data = base64.b64decode(self.datas)
            data_file = io.StringIO(csv_data.decode("utf-8"))
            data_file.seek(0)
            file_reader = []

            csv_reader = csv.reader(data_file, delimiter=',')
            file_reader.extend(csv_reader)

            values = {}

            for i in range(len(file_reader)):
                columns = list(map(str, file_reader[i]))
                values = dict(zip(keys, columns))
                if bool(values):
                    if i == 0:
                        continue
                    else:
                        vals = self._validate_bank_statement_line_vals({
                            'date': columns[0],
                            'payment_ref': columns[1],
                            'partner_name': columns[2],
                            'ref': columns[3],
                            'narration': columns[4],
                            'amount': columns[5],
                            'account_number': columns[6]
                            })
                        values.update(vals)
                        transaction_list.append(values)
        except Exception as e:
            raise UserError(_("Invalid CSV file! Here is detail error:\n%s") % str(e))

        statement_vals.update({
            'transactions': transaction_list
            })
        bank_account_number = None
        currency = None
        return currency, bank_account_number, [statement_vals]
