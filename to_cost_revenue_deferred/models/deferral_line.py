from odoo import fields, models, api, _
from odoo.tools import float_compare
from odoo.exceptions import UserError


class DeferralLine(models.Model):
    _name = 'cost.revenue.deferral.line'
    _description = 'Cost Revenue Deferral Lines'

    name = fields.Char(string="Name", required=True)
    sequence = fields.Integer(string="Sequence", required=True)
    deferral_id = fields.Many2one('cost.revenue.deferral', string="Deferral")
    state = fields.Selection(related='deferral_id.state', string='Status')
    amount = fields.Float(string="Current Deferral", digits='Account', required=True)
    remaining_value = fields.Float(string="Next Deferral Period", digits='Account', required=True)
    distributed_value = fields.Float(string="Amount Already Distributed", digits='Account', required=True)
    deferral_date = fields.Date(string="Deferral Date")
    move_id = fields.Many2one('account.move', string="Deferral Entry")
    move_check = fields.Boolean(string="Journal Entry", compute='_compute_move_check', store=True)
    move_posted_check = fields.Boolean(compute='_compute_move_posted', string='Posted', tracking=True, store=True)

    @api.depends('move_id')
    def _compute_move_check(self):
        for r in self:
            r.move_check = bool(r.move_id)

    @api.depends('move_id.state')
    def _compute_move_posted(self):
        for r in self:
            r.move_posted_check = True if r.move_id and r.move_id.state == 'posted' else False

    def create_move(self, post_move=True):
        post_move = self._context.get('auto_post', post_move)
        created_moves = self.env['account.move']
        for line in self:
            category_id = line.deferral_id.deferral_category_id
            deferral_date = self.env.context.get('deferral_date') or line.deferral_date or fields.Date.context_today(self)
            company_currency = line.deferral_id.company_id.currency_id
            current_currency = line.deferral_id.currency_id
            amount = current_currency._convert(line.amount, company_currency, line.deferral_id.company_id, deferral_date)
            sign = (line.deferral_id.type == 'cost' and 1) or -1
            amount = amount * sign
            deferral_name = line.deferral_id.name + ' (%s/%s)' % (line.sequence, len(line.deferral_id.deferral_line_ids))
            reference = line.deferral_id.name
            journal_id = category_id.journal_id.id
            partner_id = line.deferral_id.partner_id.id
            prec = self.env['decimal.precision'].precision_get('Account')
            move_line_1 = {
                'name': deferral_name,
                'ref': reference,
                'account_id': category_id.deferred_account_id.id,
                'debit': 0.0 if float_compare(amount, 0.0, precision_digits=prec) > 0 else -amount,
                'credit': amount if float_compare(amount, 0.0, precision_digits=prec) > 0 else 0.0,
                'journal_id': journal_id,
                'partner_id': partner_id,
                'currency_id': company_currency != current_currency and current_currency.id or False,
                'amount_currency': company_currency != current_currency and -sign * line.amount or 0.0,
                'date': deferral_date,
                'deferral_id': line.deferral_id.id
            }
            move_line_2 = {
                'name': deferral_name,
                'ref': reference,
                'account_id': category_id.recognition_account_id.id,
                'credit': 0.0 if float_compare(amount, 0.0, precision_digits=prec) > 0 else -amount,
                'debit': amount if float_compare(amount, 0.0, precision_digits=prec) > 0 else 0.0,
                'journal_id': journal_id,
                'partner_id': partner_id,
                'currency_id': company_currency != current_currency and current_currency.id or False,
                'amount_currency': company_currency != current_currency and sign * line.amount or 0.0,
                'analytic_account_id': category_id.account_analytic_id.id,
                'analytic_tag_ids':[(4, tag.id) for tag in category_id.sudo().analytic_tag_ids],
                'date': deferral_date,
                'deferral_id': line.deferral_id.id,
            }
            move_vals = {
                'date': deferral_date,
                'ref': reference,
                'journal_id': journal_id,
                'line_ids': [(0, 0, move_line_1), (0, 0, move_line_2)],
                'auto_post': True if line.deferral_id.auto_create_move else False,
            }
            ctx = dict(self.env.context)
            # Within the context of the deferral,
            # this default value is for the type of the deferral, not the type of the invoice.
            # This has to be cleaned from the context before creating the invoice,
            # otherwise it tries to create the invoice with the type of the deferral.
            ctx.pop('default_type', None)
            move = self.env['account.move'].with_context(ctx).create(move_vals)
            line.write({'move_id': move.id, 'move_check': True})
            created_moves |= move

        if post_move and created_moves:
            self.post_lines_and_close_deferral()
            created_moves.post()
        return [x.id for x in created_moves]

    def post_lines_and_close_deferral(self):
        # we re-evaluate the deferrals to determine whether we can close them
        for line in self:
            line.log_message_when_posted()
            deferral = line.deferral_id
            if deferral.currency_id.is_zero(deferral.value_residual) and deferral.deferral_line_ids.filtered(lambda r: not r.move_posted_check):
                deferral.message_post(body=_("Document closed."))
                deferral.write({'state': 'close'})

    def log_message_when_posted(self):

        def _format_message(message_description, tracked_values):
            message = ''
            if message_description:
                message = '<span>%s</span>' % message_description
            for name, values in tracked_values.items():
                message += '<div> &nbsp; &nbsp; &bull; <b>%s</b>: ' % name
                message += '%s</div>' % values
            return message

        for line in self:
            if line.move_id and line.move_id.state == 'draft':
                partner_name = line.deferral_id.partner_id.name
                currency_name = line.deferral_id.currency_id.name
                msg_values = {_('Currency'): currency_name, _('Amount'): line.amount}
                if partner_name:
                    msg_values[_('Partner')] = partner_name
                msg = _format_message(_('Deferral line posted.'), msg_values)
                line.deferral_id.message_post(body=msg)

    def unlink(self):
        for r in self:
            if r.move_id and r.move_id.state != 'cancel':
                if r.deferral_id.deferral_category_id.type == 'cost':
                    msg = _("You cannot delete cost deferral lines while its journal entries status is not Cancel.")
                else:
                    msg = _("You cannot delete revenue deferral lines while its journal entries status is not Cancel.")
                raise UserError(msg)
        return super(DeferralLine, self).unlink()

    def cron_auto_create_move_deferral(self):
        deferrals = self.env['cost.revenue.deferral'].search([('state', '=', 'open'), ('auto_create_move', '=', True)])
        deferral_lines = deferrals.deferral_line_ids.filtered(lambda r:r.deferral_date <= fields.Date.today() and not r.move_check)        
        deferral_lines.create_move()
