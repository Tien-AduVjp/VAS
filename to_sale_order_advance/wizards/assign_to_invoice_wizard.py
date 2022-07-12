from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.float_utils import float_compare


class AssignToInvoiceWizard(models.TransientModel):
    _name = 'assign.to.invoice.wizard'
    _description = 'Assign To Invoice Wizard'

    @api.model
    def _get_default_amount(self):
        amount = 0

        move_id = self._context.get('move_id', False)
        line_id = self._context.get('line_id', False)
        if move_id and line_id:
            move = self.env['account.move'].browse(move_id)
            line = self.env['account.move.line'].browse(line_id)
            if line.currency_id and line.currency_id == move.currency_id:
                amount = abs(line.amount_residual_currency)
            else:
                currency = line.company_id.currency_id
                amount = currency._convert(abs(line.amount_residual), move.currency_id, move.company_id,
                                                   line.date or fields.Date.today())
        return amount

    amount = fields.Float(string='Amount',
                          required=True,
                          default=_get_default_amount,
                          help="The amount that is assigned to invoice")

    def _check_amount(self, move_id, line_id):
        """ check the outstanding residual value in invoice currency"""
        self.ensure_one()
        move = self.env['account.move'].browse(move_id)
        line = self.env['account.move.line'].browse(line_id)
        amount = self._get_default_amount()
        if float_compare(self.amount, 0, precision_rounding=move.currency_id.rounding) <= 0:
            raise UserError(_("The amount that is assigned to invoice must be greater than 0!"))
        if float_compare(self.amount, amount, precision_rounding=move.currency_id.rounding) == 1:
            raise ValidationError(_("The amount that is assigned to invoice"
                                    " is greater than the amount for advance payment %s!") % (line.payment_id.name))

    def add(self):
        self.ensure_one()
        move_id = self._context.get('move_id', False)
        line_id = self._context.get('line_id', False)
        if move_id and line_id:
            self._check_amount(move_id, line_id)
            move = self.env['account.move'].browse(move_id)
            move.with_context(force_amount=self.amount, invoice_currency_id=move.currency_id.id).js_assign_outstanding_line(line_id)
            return {
                'type': 'ir.actions.client',
                'tag': 'reload',
            }
        return True
