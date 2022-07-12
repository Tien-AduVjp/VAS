from odoo import fields, models, _
from odoo.exceptions import ValidationError
from odoo.tools import float_compare
from odoo.tools.misc import format_date


class DeferralDisposal(models.TransientModel):
    _name = 'deferral.disposal'
    _description = 'Deferral Disposal'

    deferral_id = fields.Many2one('cost.revenue.deferral', string="Deferral", required=True)
    name = fields.Char(string="Reference")
    date = fields.Date(string="Date", required=True, default=fields.Date.today)
    reason = fields.Text(string="Reason")


    def action_disposal(self):
        self.ensure_one()
        date_formatted = format_date(self.env, self.date)
        deferral_lines = self.deferral_id.deferral_line_ids
        
        if not deferral_lines.filtered(lambda r: not r.move_check):
            raise ValidationError(_("You cannot dispose the deferral %s while its all deferral lines already have journal entries.")%(self.deferral_id.name))
        
        if not deferral_lines.filtered(lambda r:r.deferral_date <= self.date):
            raise ValidationError(_("You cannot dispose the deferral %s while it has no deferral line that the Deferral Date of which is earlier than or equal to '%s'.")
                                  % (self.deferral_id.name, date_formatted))
        
        if deferral_lines.filtered(lambda r:r.deferral_date <= self.date and not r.move_check):
            raise ValidationError(_("You cannot dispose the deferral %s while it has the deferral line earlier or equal to date '%s' without the journal entry.")
                                  % (self.deferral_id.name, date_formatted))
        
        if deferral_lines.filtered(lambda r:r.deferral_date > self.date and r.move_check):
            raise ValidationError(_("You cannot dispose the deferral %s while it has the deferral line after the date '%s' has the journal entry.")
                                  % (self.deferral_id.name, date_formatted))

        category_id = self.deferral_id.deferral_category_id
        journal_id = category_id.journal_id.id
        partner_id = self.deferral_id.partner_id.id
        prec = self.env['decimal.precision'].precision_get('Account')
        deferral_name = reference = self.deferral_id.name
        company_currency = self.deferral_id.company_id.currency_id
        current_currency = self.deferral_id.currency_id
        amount = self.deferral_id.currency_id._convert(self.deferral_id.value_residual, company_currency, self.deferral_id.company_id, self.date)
        sign = (self.deferral_id.type == 'cost' and 1) or -1
        amount = amount * sign
        move_line_1 = {
            'name': deferral_name,
            'ref': reference,
            'account_id': category_id.deferred_account_id.id,
            'debit': 0.0 if float_compare(amount, 0.0, precision_digits=prec) > 0 else -amount,
            'credit': amount if float_compare(amount, 0.0, precision_digits=prec) > 0 else 0.0,
            'journal_id': journal_id,
            'partner_id': partner_id,
            'currency_id': company_currency != current_currency and current_currency.id or False,
            'amount_currency': company_currency != current_currency and -sign * amount or 0.0,
            'date': self.date,
            'deferral_id': self.deferral_id.id
        }
        move_line_2 = {
            'name': deferral_name,
            'ref': reference,
            'account_id': self.deferral_id.deferral_category_id.recognition_account_id.id,
            'credit': 0.0 if float_compare(amount, 0.0, precision_digits=prec) > 0 else -amount,
            'debit': amount if float_compare(amount, 0.0, precision_digits=prec) > 0 else 0.0,
            'journal_id': journal_id,
            'partner_id': partner_id,
            'currency_id': company_currency != current_currency and current_currency.id or False,
            'amount_currency': company_currency != current_currency and sign * amount or 0.0,
            'analytic_account_id': category_id.account_analytic_id.id,
            'analytic_tag_ids':[(4, tag.id) for tag in category_id.sudo().analytic_tag_ids],
            'date': self.date,
            'deferral_id': self.deferral_id.id
        }
        move_vals = {
            'date': self.date,
            'ref': reference,
            'journal_id': journal_id,
            'line_ids': [(0, 0, move_line_1), (0, 0, move_line_2)],
        }
        move = self.env['account.move'].create(move_vals)
        
        deferral_lines = deferral_lines.filtered(lambda r:r.deferral_date > self.date).unlink()
        self.deferral_id.write({'state': 'close'})
        return move
