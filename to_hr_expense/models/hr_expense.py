from odoo import models, fields, api, _
from odoo.exceptions import UserError


class HrExpense(models.Model):
    _inherit = "hr.expense"
    
    vendor_id = fields.Many2one('res.partner', readonly=False, states={'reported': [('readonly', True)],
                                                                       'approved': [('readonly', True)],
                                                                       'done': [('readonly', True)],
                                                                       'refused': [('readonly', True)]},
        domain="['|', ('company_id', '=', False), ('company_id', '=', company_id)]", string='Vendor')
    to_invoice = fields.Boolean('Create Invoice?', help="If checked, field Vendor is required, and this expense will be the input invoice")
    
    @api.onchange('payment_mode')
    def _onchange_set_to_invoice(self):
        if self.payment_mode == 'own_account':
            self.to_invoice = True
        else: 
            self.to_invoice = False

    def _prepare_move_values(self):
        """ Set data to prepare move lines
        Type: type = 'in_invoice'
        Partner:  partner_id = self.vendor_id.id
        """
        res = super(HrExpense, self)._prepare_move_values()

        if self.payment_mode == 'own_account':
            if self.to_invoice:
                res['type'] = 'in_invoice'
                res['invoice_date'] = res['date']
            if self.vendor_id:
                res['partner_id'] = self.vendor_id.id
        return res

    def _get_account_move_line_values(self):
        """
        When choose to_invoice (Is Invoice) = True, 
        Set type move line = in_invoice,  at def _prepare_move_values()
        Set `exclude_from_invoice_tab` = True/False to distinguish `Invoice Lines` and `Journal Item`
        """
        res = super(HrExpense, self)._get_account_move_line_values()

        """
        self has many record
        Only to_invoice = True => set exclude_from_invoice_tab
        check:  payment_mode = 'own_account'
                to_invoice = True
                number of set(to_invoice) = 1
        """
        payment_mode = self.mapped('payment_mode')
        to_invoice = self.mapped('to_invoice')
        number = len(set(to_invoice))

        if number == 1 and to_invoice[0] and payment_mode[0] == 'own_account':
            for r_list in res.values():
                for r in r_list:               
                    expense_id = r['expense_id']
                    account = self.filtered(lambda r: r.id == expense_id)._get_expense_account_source()
                    
                    if int(r['account_id']) == account.id:
                        r['exclude_from_invoice_tab'] = False
                    else:
                        r['exclude_from_invoice_tab'] = True
        
        # In case paid by company and Lump-sum Payment
        # Make sure all expenses are on the same expense sheet
        # This expense sheet was paid by company, all expense lines of this sheet will be paid by only a payment
        sheet_id = self.sheet_id
        if len(sheet_id) == 1 and sheet_id.payment_mode == 'company_account' and sheet_id.aggregate_payments:
            move_line_values = []
            move_line_dsts = []
            for r in self:
                for line in res.get(r.id, []):
                    if line.get('quantity', 0) > 0:
                        move_line_values.append(line)
                    else:
                        move_line_dsts.append(line)
            if move_line_dsts:
                currency_set = set()
                for line in move_line_dsts:
                    currency_set.add(line.get('currency_id', False) and line['currency_id'] or 0)
                if len(currency_set) > 1:
                    raise UserError(_("""An expense sheet of multiple currencies with lump-sum payment option"""
                                      """ enabled is not supported. Please either uncheck the option Lump-sum Payment"""
                                      """ or separate the sheet into multiple ones of single currency."""))
                new_move_line_dst = {
                    'name': sheet_id.employee_id.name + ': ' + sheet_id.name,
                    'debit': sum(line.get('debit', 0) for line in move_line_dsts),
                    'credit': sum(line.get('credit', 0) for line in move_line_dsts),
                    'account_id': move_line_dsts[0].get('account_id', False),
                    'date_maturity': move_line_dsts[0].get('date_maturity', False),
                    'amount_currency': sum(line.get('amount_currency', 0) for line in move_line_dsts),
                    'currency_id': move_line_dsts[0].get('currency_id', False),
                    'partner_id': move_line_dsts[0].get('partner_id', False),
                }
                move_line_values.append(new_move_line_dst)
            return move_line_values
        
        return res
    
    def action_move_create(self):
        sheet_id = self.sheet_id
        if len(sheet_id) == 1 and sheet_id.payment_mode == 'company_account' and sheet_id.aggregate_payments:
            move_group_by_sheet = self._get_account_move_by_sheet()

            move_line_values = self._get_account_move_line_values()
            
            company_currency = sheet_id.company_id.currency_id
            different_currency = sheet_id.currency_id != company_currency
            move = move_group_by_sheet.get(sheet_id.id, self.env['account.move'])
            move_line_dst = move_line_values[-1]
            total_amount = move_line_dst['debit'] or -move_line_dst['credit']
            total_amount_currency = move_line_dst['amount_currency']
            if not sheet_id.bank_journal_id.default_credit_account_id:
                raise UserError(_("No credit account found for the %s journal, please configure one.") % (sheet_id.bank_journal_id.name))
            journal = sheet_id.bank_journal_id
            # create payment
            payment_methods = journal.outbound_payment_method_ids if total_amount < 0 else journal.inbound_payment_method_ids
            journal_currency = journal.currency_id or journal.company_id.currency_id
            sequence_code = 'account.payment.supplier.invoice'
            payment = self.env['account.payment'].create({
                'name': self.env['ir.sequence'].next_by_code(sequence_code, sequence_date=move.date),
                'payment_method_id': payment_methods and payment_methods[0].id or False,
                'payment_type': 'outbound' if total_amount < 0 else 'inbound',
                'partner_id': sheet_id.employee_id.sudo().address_home_id.commercial_partner_id.id,
                'partner_type': 'supplier',
                'journal_id': journal.id,
                'payment_date': move.date,
                'state': 'draft',
                'currency_id': sheet_id.currency_id.id if different_currency else journal_currency.id,
                'amount': abs(total_amount_currency) if different_currency else abs(total_amount),
            })
            for line in move_line_values:
                line['payment_id'] = payment.id 
            
            # link move lines to move, and move to expense sheet
            move.write({'line_ids': [(0, 0, line) for line in move_line_values]})
            sheet_id.write({'account_move_id': move.id})

            sheet_id.paid_expense_sheets()
            if payment.journal_id.post_at == 'pay_val':
                payment.write({'state':'reconciled'})
            elif payment.journal_id.post_at == 'bank_rec':
                payment.write({'state':'posted'})
            
            # post the moves
            if journal.post_at != 'bank_rec':
                move.post()

            return move_group_by_sheet
        else:
            return super(HrExpense, self).action_move_create()
    
    @api.model
    def _update_to_invoice_status_for_existing_expenses(self):
        # this method is to set 'to_invoice' field to False with existing records before installing this module to avoid exception of field 'Vendor'  required
        expenses_need_update =  self.search(['|', ('payment_mode', '!=', 'own_account'), 
                     '&', ('sheet_id', '!=', False), ('vendor_id', '=', False)])
        expenses_need_update.write({'to_invoice':False})
    