from odoo import models, fields, api, _
from odoo.exceptions import UserError


class HrExpense(models.Model):
    _inherit = 'hr.expense'

    vendor_id = fields.Many2one('res.partner', readonly=False, states={'reported': [('readonly', True)],
                                                                       'approved': [('readonly', True)],
                                                                       'done': [('readonly', True)],
                                                                       'refused': [('readonly', True)]},
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]", string='Vendor')
    to_invoice = fields.Boolean(string='Create Invoice?', help="If checked, field Vendor is required, and this expense will be the input invoice")
    reference = fields.Char(help="Allow user to input bill reference. Paid by employee, "
                            "expenses with the same vendor and reference will be created in the same invoice if they are on the same expense sheet.")

    # Override compute amount_residual because we use move_ids instead of account_move_id
    amount_residual = fields.Monetary(string='Amount Due', compute='_compute_amount_residual', compute_sudo=True)

    @api.depends(
        'currency_id',
        'sheet_id.move_ids.line_ids',
        'sheet_id.move_ids.line_ids.amount_residual',
        'sheet_id.move_ids.line_ids.amount_residual_currency',
        'sheet_id.move_ids.line_ids.account_internal_type')
    def _compute_amount_residual(self):
        for r in self:
            if not r.sheet_id:
                r.amount_residual = r.total_amount
                continue
            if not r.currency_id or r.currency_id == r.company_id.currency_id:
                residual_field = 'amount_residual'
            else:
                residual_field = 'amount_residual_currency'

            if r.payment_mode == 'company_account':
                payment_term_lines = r.sheet_id.move_ids.line_ids \
                    .filtered(lambda line: line.expense_id == r and line.account_internal_type in ('receivable', 'payable'))
            else:
                payment_term_lines = r.sheet_id.move_ids.line_ids \
                    .filtered(lambda line: line.expense_id == r and line.account_id.id == r.employee_id.sudo().address_home_id.property_account_payable_id.id)
            r.amount_residual = -sum(payment_term_lines.mapped(residual_field))

    def _prepare_move_values(self):
        """ Set data to prepare move lines
        Type: type = 'in_invoice'
        Partner:  partner_id = self.vendor_id.id
        """
        res = super(HrExpense, self)._prepare_move_values()

        if self.to_invoice:
            res['move_type'] = 'in_invoice'
            res['invoice_date'] = res['date']
            res['journal_id'] = self.sheet_id.vendor_bill_journal_id.id or self.sheet_id.journal_id.id
        if self.vendor_id:
            res['partner_id'] = self.vendor_id.id
        res['ref'] = self.reference or self.sheet_id.name
        return res

    def _get_account_move_line_values(self):
        """
        When choose to_invoice (Is Invoice) = True,
        Set type move line = in_invoice,  at def _prepare_move_values()
        Set `exclude_from_invoice_tab` = True/False to distinguish `Invoice Lines` and `Journal Item`
        """
        res = super(HrExpense, self)._get_account_move_line_values()

        # TODO: remove in 15.0 because it exclude_from_invoice_tab added into destination move line from 15.0
        # Ref. https://github.com/odoo/odoo/pull/65528
        for r in self:
            for line in res.get(r.id, []):
                account_dst = r._get_expense_account_destination()
                if line.get('account_id', False) == account_dst:
                    line['exclude_from_invoice_tab'] = True

        """
        self has many record
        Only to_invoice = True => set exclude_from_invoice_tab
        check:  to_invoice = True
                number of set(to_invoice) = 1
        """
        to_invoice = self.mapped('to_invoice')
        number = len(set(to_invoice))

        if number == 1 and to_invoice[0]:
            for expense_id, r_list in res.items():
                expense = self.filtered(lambda e: e.id == expense_id)
                account = expense._get_expense_account_source()
                for r in r_list:
                    r['partner_id'] = expense.vendor_id.id
                    if int(r['account_id']) == account.id:
                        r['exclude_from_invoice_tab'] = False
                    else:
                        r['exclude_from_invoice_tab'] = True
        return res

    def action_move_create(self):
        sheet = self.sheet_id
        if len(sheet) == 1:
            if sheet.has_invoice:
                # In the expense report, there are many expense of different suppliers
                moves_group_by_sheet = {}
                for vendor in self.vendor_id:
                    # Same vendor
                    vendor_expenses = self.filtered(lambda e: e.vendor_id.id == vendor.id)
                    references = set(vendor_expenses.mapped('reference'))
                    for reference in references:
                        # Same reference
                        expenses = vendor_expenses.filtered(lambda e: e.reference == reference)
                        move_group_by_sheet = expenses._get_account_move_by_sheet()
                        for key, value in move_group_by_sheet.items():
                            if key not in moves_group_by_sheet.keys():
                                moves_group_by_sheet.update(move_group_by_sheet)
                            else:
                                moves_group_by_sheet[key] |= value
                        move_line_values_by_expense = expenses._get_account_move_line_values()
                        for expense in expenses:
                            move = move_group_by_sheet[expense.sheet_id.id]
                            move_line_values = move_line_values_by_expense.get(expense.id)
                            move.write({'line_ids': [(0, 0, line) for line in move_line_values], 'hr_expense_sheet_id': expense.sheet_id.id})
                            expense.sheet_id.write({
                                'account_move_id': move.id,
                            })
                        for move in move_group_by_sheet.values():
                            move.action_post()
                return moves_group_by_sheet
            else:
                move_group_by_sheet = super(HrExpense, self).action_move_create()
                move = move_group_by_sheet.get(sheet.id, self.env['account.move'])
                move.write({'hr_expense_sheet_id': sheet.id})
                return move_group_by_sheet
        else:
            return super(HrExpense, self).action_move_create()

    @api.model
    def _update_to_invoice_status_for_existing_expenses(self):
        # this method is to set 'to_invoice' field to False with existing records before installing this module to avoid exception of field 'Vendor'  required
        expenses_need_update = self.search(['|', ('payment_mode', '!=', 'own_account'),
                     '&', ('sheet_id', '!=', False), ('vendor_id', '=', False)])
        expenses_need_update.write({'to_invoice':False})

    def _get_expense_account_destination(self):
        account_dest = super(HrExpense, self)._get_expense_account_destination()
        if self.to_invoice and self.vendor_id:
            account_dest = self.vendor_id.property_account_payable_id.id
        return account_dest
