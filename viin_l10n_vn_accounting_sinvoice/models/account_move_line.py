from odoo import models
from odoo.tools import float_round


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    def _prepare_sinvoice_line_data(self, line_data):

        self.ensure_one()
        data = {
            'lineNumber': line_data['lineNumber']
        }
        if self.display_type:
            data.update({
                'selection': 2,
                'itemName': self.name
            })
        else:
            if line_data['itemCode']:
                data.update({'itemCode': line_data['itemCode']})
            data.update({
                'itemName': line_data['itemName'],
                'unitName': line_data['unitName'],
                'unitPrice': line_data['unitPrice'],
                'quantity': line_data['quantity'],
                'itemTotalAmountWithoutTax': line_data['itemTotalAmountWithoutVat'],
                'taxPercentage': line_data['vatPercentage'],
                'taxAmount': line_data['vatAmount'],
                'discount': 0,
                'itemDiscount': 0,
                'itemTotalAmountWithTax': line_data['itemTotalAmountWithVat']
            })
            if self.move_id.move_type == 'out_refund':
                data.update({
                    'adjustmentTaxAmount': line_data['vatAmount'],
                    'isIncreaseItem': False,
                    'itemTotalAmountAfterDiscount': line_data['itemTotalAmountWithVat']
            })
            if self.move_id.einvoice_api_version == 'v2':
                [data.pop(key, False) for key in ('itemDiscount', 'itemTotalAmountWithTax')]
        return data
