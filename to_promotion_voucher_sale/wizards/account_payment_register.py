from odoo import models, api, _
from odoo.exceptions import UserError


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    @api.model
    def default_get(self, fields_list):
        """ Hard code:
        Handling the case that the invoice has 2 lines, which are receivable or payable
        """
        if self._context.get('active_model') == 'account.move':
            lines = self.env['account.move'].browse(self._context.get('active_ids', [])).line_ids
        elif self._context.get('active_model') == 'account.move.line':
            lines = self.env['account.move.line'].browse(self._context.get('active_ids', []))
        else:
            raise UserError(_(
                "The register payment wizard should only be called on account.move or account.move.line records."
            ))
        if any(lines.product_id.mapped('is_promotion_voucher')):
            fields_list.remove('line_ids')
            res = super(AccountPaymentRegister, self).default_get(fields_list)

            lines -= lines.filtered(
                lambda line: (
                    line.product_id.property_account_income_id
                    and line.account_id.id == line.product_id.property_account_income_id.id
                )
                or (
                    line.product_id.categ_id.property_account_income_categ_id
                    and line.account_id.id
                    == line.product_id.categ_id.property_account_income_categ_id.id
                )
            )

            if 'journal_id' in res and not self.env['account.journal'].browse(res['journal_id'])\
                    .filtered_domain([('company_id', '=', lines.company_id.id), ('type', 'in', ('bank', 'cash'))]):
                # default can be inherited from the list view, should be computed instead
                del res['journal_id']

            # Keep lines having a residual amount to pay.
            available_lines = self.env['account.move.line']
            for line in lines:
                if line.move_id.state != 'posted':
                    raise UserError(_("You can only register payment for posted journal entries."))

                if line.account_internal_type not in ('receivable', 'payable'):
                    continue
                if line.currency_id:
                    if line.currency_id.is_zero(line.amount_residual_currency):
                        continue
                else:
                    if line.company_currency_id.is_zero(line.amount_residual):
                        continue
                available_lines |= line

            # Check.
            if not available_lines:
                raise UserError(_("You can't register a payment because there is nothing left to pay on the selected journal items."))
            if len(lines.company_id) > 1:
                raise UserError(_("You can't create payments for entries belonging to different companies."))
            if len(set(available_lines.mapped('account_internal_type'))) > 1:
                raise UserError(_("You can't register payments for journal items being either all inbound, either all outbound."))

            res['line_ids'] = [(6, 0, available_lines.ids)]
            return res
        else:
            return super(AccountPaymentRegister, self).default_get(fields_list)
