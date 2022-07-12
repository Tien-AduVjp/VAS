# -*- coding: utf-8 -*-

import logging
import tempfile
import binascii

from odoo import models, fields, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

try:
    import xlrd
except ImportError:
    _logger.debug('Cannot `import xlrd`.')


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    def _check_xlsx(self):
        return self.mimetype == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'

    def _parse_as_bank_statement(self):
        self.ensure_one()
        if not self._check_xlsx():
            return super(IrAttachment, self)._parse_as_bank_statement()
        statement_vals = {}
        transaction_list = []
        try:
            fp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
            fp.write(binascii.a2b_base64(self.datas))
            fp.seek(0)
            values = {}
            workbook = xlrd.open_workbook(fp.name)
            sheet = workbook.sheet_by_index(0)

            for row_no in range(sheet.nrows):
                values = {}
                if row_no <= 0:
                    map(lambda row: row.value.encode('utf-8'), sheet.row(row_no))
                else:
                    columns = list(map(
                        lambda row: isinstance(row.value, bytes) and row.value.encode('utf-8') or str(row.value),
                        sheet.row(row_no)
                        )
                    )
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
            raise UserError(_("Invalid Excel .xlsx file! Here is detail error:\n%s") % str(e))
        statement_vals.update({
            'transactions': transaction_list
            })
        bank_account_number = None
        currency_lst = None
        return currency_lst, bank_account_number, [statement_vals]
