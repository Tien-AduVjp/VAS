from odoo import models, api, _
from odoo.exceptions import ValidationError, UserError


class ReportAccountMove(models.AbstractModel):
    _name = 'report.viin_l10n_vn_payment_print.report_account_move'
    _description = 'Account Move Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        moves = self.env['account.move'].browse(docids)
        for record in moves:
            if record.state in ('draft', 'cancel'):
                raise ValidationError(_("There are a few Journal Entries not in state Posted. You can post it and try again."))
            if record.journal_id.type not in ('bank', 'cash'):
                raise UserError(_('Only payments could be printed.'))
        return {
                'doc_ids': docids,
                'doc_model': 'account.move',
                'docs': moves,
                'report_type': data.get('report_type', '') if data else '',
            }
