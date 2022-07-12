from odoo import models, fields, _
from odoo.exceptions import ValidationError, UserError


class HrExpenseSheet(models.Model):
    _inherit = "hr.expense.sheet"
    
    payment_ids = fields.One2many('account.payment', 'expense_sheet_id', string='Payments')
    payments_count = fields.Integer(string='Payments Count', compute='_compute_payment_count')
    # TODO: rename `aggregate_payments` into `lumpsum_payment` in master/15+
    aggregate_payments = fields.Boolean(string='Lump-sum Payment?', default=True,
        help="If checked, in case this expense sheet was paid by company,"
        " all expense lines of this sheet will be paid by one single payment.")

    def _compute_payment_count(self):
        payments_data = self.env['account.payment'].sudo().read_group([('expense_sheet_id', 'in', self.ids)], ['expense_sheet_id'], ['expense_sheet_id'])
        mapped_data = dict([(dict_data['expense_sheet_id'][0], dict_data['expense_sheet_id_count']) for dict_data in payments_data])
        for r in self:
            r.payments_count = mapped_data.get(r.id, 0)

    def action_sheet_move_create(self):
        res = super(HrExpenseSheet, self).action_sheet_move_create()
        for move in res.values():
            payments = move.line_ids.payment_id
            expense_sheets = self.filtered(lambda x: x.account_move_id == move)
            if expense_sheets:
                payments.write({'expense_sheet_id': expense_sheets[0].id})
        return res

    def action_view_payments(self):
        action = self.env.ref('account.action_account_payments_payable')
        result = action.read()[0]

        # choose the view_mode accordingly
        if self.payments_count != 1:
            result['domain'] = "[('expense_sheet_id', 'in', %s)]" % str(self.ids)
        elif self.payments_count == 1:
            res = self.env.ref('account.view_account_payment_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = self.payment_ids.id
        return result

    def action_submit_sheet(self):
        """
        check lines: partner, to_invoice on all lines are the same
        """
        for r in self:
            vendor = r.expense_line_ids.mapped('vendor_id')        
            paid_by = r.expense_line_ids.mapped('payment_mode')
            invoice = r.expense_line_ids.filtered(lambda x: x.to_invoice)
            
            if invoice and invoice != r.expense_line_ids:
                raise ValidationError(_("Expenditures must be set to the same 'Create Invoice?' value (either billed or invoiced)"))      
            if 'own_account' in paid_by and len(vendor) > 1:
                raise ValidationError(_("Vendor of all expense lines in this sheet should be the same."))

        super(HrExpenseSheet, self).action_submit_sheet()

    def action_cancel(self):
        if self.account_move_id and self.account_move_id.state != 'cancel':
            raise UserError(_("You cannot cancel a posted expense. Please cancel this Journal Entry first: %s")%self.account_move_id.display_name)
        if self.payment_ids.filtered(lambda r:r.state != 'cancelled'):
            raise UserError(_("You cannot cancel a paid expense. Please cancel all Payments of this expense first"))
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'hr.expense.refuse.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'hr_expense_refuse_model':'hr.expense.sheet'}
        }
    
    def unlink(self):
        for r in self:
            if r.account_move_id or r.payment_ids:
                raise UserError(_("You cannot delete the expense '%s' which has been posted once entry '%s' !")%(r.name, r.account_move_id.name))
        return super(HrExpenseSheet, self).unlink()
