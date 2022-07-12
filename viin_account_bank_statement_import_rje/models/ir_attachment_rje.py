# -*- coding: utf-8 -*-

import base64
import re
import json
import logging

from odoo import fields, models, _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)

try:
    import mt940
except ImportError:
    _logger.warning("The mt-940 python library is not installed, rje import will not work. Please try the following command `pip install mt-940`")


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    def _check_csv(self):
        self.ensure_one()
        return self.mimetype == 'text/csv'

    def _check_rje(self):
        return self.name and self.name.lower().strip().endswith('.rje')

    def format_rje_data(self, data_file):
        """ Only Vietcombank
        From :
            :28C: Statement number/ Sequence number
            1/1
            :60M: Opening Balance
            C200601VND1,734,894,950.00
            :61: Statement Line
            200702C2,199,000.00//0040 - 01023
            :62M: Closing Balance
            C200703VND1,734,894,950.00
        To:
            :28C:1/1
            :60M:C200601VND1734894950,00
            :61:200702C2199000,00NMSC0040 - 01023
            :62M:C200703VND1734894950,00
        """
        RegEx_20 = b":20: Transaction Reference Number\r\n"
        new_data = re.sub(RegEx_20, b":20:", data_file)

        RegEx_25 = b":25: Account Identification\r\n"
        new_data = re.sub(RegEx_25, b":25:", new_data)

        RegEx_28C = b":28C: Statement number/ Sequence number\r\n"
        new_data = re.sub(RegEx_28C, b":28C:", new_data)

        RegEx_60M = b":60M: Opening Balance\r\n"
        new_data = re.sub(RegEx_60M, b":60M:", new_data)

        RegEx_61 = b":61: Statement Line\r\n"
        new_data = re.sub(RegEx_61, b":61:", new_data)

        RegEx_86 = b":86: Information to Account Owner\r\n"
        new_data = re.sub(RegEx_86, b":86:", new_data)

        RegEx_62M = b":62M: Closing Balance\r\n"
        new_data = re.sub(RegEx_62M, b":62M:", new_data)

        new_data = new_data.decode("utf-8")

        # check data in VCB file
        lines = new_data.splitlines();
        out_lines = []
        for line in lines:
            if line.startswith(':61:') or line.startswith(':60M:') or line.startswith(':62M:'):
                new_line = line.replace(',', '')
                new_line = new_line.replace('.', ',')
                if line.startswith(':61:'):
                    new_line = new_line.replace('//', 'NMSC')
                out_lines.append(new_line)
            else:
                out_lines.append(line)

        listToStr = '\r\n'.join([str(elem) for elem in out_lines])
        return listToStr

    def _parse_as_bank_statement(self):
        self.ensure_one()
        if not self._check_rje():
            return super(IrAttachment, self)._parse_as_bank_statement()
        try:
            data_file = base64.b64decode(self.datas)
            if re.search(b":20:ACB", data_file):
                data_file = data_file.decode('utf-8')
            else:
                """
                Except for ACB, I have not found a rule for other banks except VCB.
                """
                data_file = self.format_rje_data(data_file)
            transactions = mt940.models.Transactions()
            transactions.parse(data_file)
            json_string = json.dumps(transactions, indent=4, cls=mt940.JSONEncoder)
            data = json.loads(json_string)
            account_identification = data.get('account_identification')
            vals_bank_statement = {}
            account_lst = [account_identification] if account_identification else []
            currency_lst = set()

            """
            ACB : final_opening_balance - final_closing_balance                    <F>
            VCB : intermediate_opening_balance - intermediate_closing_balance      <M>
            """
            temp_opening = data.get('final_opening_balance') or data.get('intermediate_opening_balance')
            temp_closing = data.get('final_closing_balance') or data.get('intermediate_closing_balance')

            currency_lst.add(temp_opening and temp_opening.get('amount').get('currency'))
            currency_lst.add(temp_closing and temp_closing.get('amount').get('currency'))
            transaction_lines = []
            today_date_str = fields.Date.to_string(fields.Date.today())
            sum_amount = 0
            for transaction in data.get('transactions', []):
                currency_lst.add(transaction.get('currency'))
                line_vals = self._validate_bank_statement_line_vals({
                    'sequence': len(transaction_lines) + 1,
                    'date': fields.Date.from_string(transaction.get('date', today_date_str)),
                    'payment_ref': transaction.get('transaction_details', ''),
                    'ref': transaction.get('customer_reference', ''),
                    'unique_import_id': transaction.get('customer_reference', ''),
                    'amount': float(transaction.get('amount').get('amount', 0.0)),
                    'currency': transaction.get('amount').get('currency', False),
                    'account_number': transaction.get('bank_reference'),
                    'transaction_type': transaction.get('id'),
                    'narration': transaction.get('transaction_details'),
                })
                sum_amount += float(line_vals['amount'])
                transaction_lines.append(line_vals)
            vals_bank_statement.update({
                'transactions': transaction_lines
            })
            if temp_closing:
                vals_bank_statement['balance_start'] = float(temp_closing.get('amount').get('amount')) - sum_amount
                vals_bank_statement['balance_end_real'] = float(temp_closing.get('amount').get('amount'))
                vals_bank_statement['date'] = fields.Date.from_string(temp_closing.get('date', today_date_str))

            if account_lst and len(account_lst) == 1:
                account_lst = account_lst.pop()
                currency_lst = currency_lst.pop()
            else:
                account_lst = None
                currency_lst = None
            return currency_lst, account_lst, [vals_bank_statement]
        except Exception as e:
            raise UserError(_("Could not import the RJE file. It could be an invalid RJE format file!\nHere is details:\n%s") % str(e))
