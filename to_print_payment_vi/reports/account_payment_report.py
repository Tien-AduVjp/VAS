from odoo import models, api, _
from odoo.exceptions import ValidationError


class ReportPayment(models.AbstractModel):
    _name = 'report.to_print_payment_vi.report_accountpayment'
    _description = 'Account payment rerport'

    @api.model
    def _get_report_values(self, docids, data=None):
        payments = self.env['account.payment'].browse(docids)
        for record in payments:
            if record.state in ('draft', 'cancelled'):
                raise ValidationError(_('There are a few Payments not in state Validated or Reconciled. You can post it and try again.'))
        return {
                'doc_ids': docids,
                'doc_model': 'account.payment',
                'docs': payments,
                'report_type': data.get('report_type', '') if data else '',
            }
