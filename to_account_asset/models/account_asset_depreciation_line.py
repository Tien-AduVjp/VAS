from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_compare


class AccountAssetDepreciationLine(models.Model):
    _name = 'account.asset.depreciation.line'
    _description = 'Asset Depreciation Line'
    _order = 'depreciation_date, sequence'

    name = fields.Char(string='Depreciation Name', required=True, index=True)
    sequence = fields.Integer(required=True)
    asset_id = fields.Many2one('account.asset.asset', string='Asset', required=True, ondelete='cascade')
    parent_state = fields.Selection(related='asset_id.state', string='State of Asset', readonly=False)
    amount = fields.Float(string='Current Depreciation', digits=0, required=True)
    remaining_value = fields.Float(string='Next Period Depreciation', digits=0, required=True)
    depreciated_value = fields.Float(string='Cumulative Depreciation', required=True)
    depreciation_date = fields.Date('Depreciation Date', index=True)
    move_id = fields.Many2one('account.move', string='Depreciation Entry')
    move_check = fields.Boolean(compute='_compute_move_check', string='Depreciation Entry Status', store=True,
                                help="""Red color: The depreciation is not already linked to a journal entry.
                                Yellow color: The depreciation is already linked to a journal entry that is in draft state.
                                Green color: The depreciation is already linked to a journal entry that is in posted state.
                                """)
    move_posted_check = fields.Boolean(compute='_compute_move_posted_check', string='Posted', store=True)
    disposal = fields.Boolean(string='Asset Stopped Depreciating', readonly=True,
                              help="This indicates that the line that asset is stopped depreciating,"
                              " created when the asset is set to close/stock_in/sold/disposed state.")
    method_period = fields.Integer(string='Number of Months in a Period',
                                   readonly=True,
                                   help="This technical field to calculate start date and end date of this depreciation line"
                                   )

    @api.depends('move_id.asset_depreciation_ids')
    def _compute_move_check(self):
        for r in self:
            r.move_check = bool(r.move_id)

    @api.depends('move_id.state')
    def _compute_move_posted_check(self):
        for r in self:
            r.move_posted_check = True if r.move_id.state == 'posted' else False

    def create_move(self, post_move=True):
        created_moves = self.env['account.move']
        for r in self.exists():
            if r.move_id:
                raise UserError(_('This depreciation is already linked to a journal entry. Please post or delete it.'))
            move_vals = r._prepare_move()
            # Within the context of an invoice,
            # this default value is for the type of the invoice, not the type of depreciation entries.
            # This has to be cleaned from the context before creating depreciation entries
            # otherwise it tries to create the depreciation entries with the type of in_invoice.
            move = self.env['account.move'].with_context(default_move_type='entry').create(move_vals)
            r.write({'move_id': move.id, 'move_check': True})
            created_moves |= move

        if post_move and created_moves:
            created_moves._post()
        return [x.id for x in created_moves]

    def _prepare_move(self):
        self.ensure_one()
        category_id = self.asset_id.category_id
        analytic_account_id = self.asset_id.sudo().analytic_account_id
        analytic_tag_ids = self.asset_id.sudo().analytic_tag_ids
        depreciation_date = self.env.context.get('depreciation_date') or self.depreciation_date or fields.Date.context_today(self)
        company_currency = self.asset_id.company_id.currency_id
        current_currency = self.asset_id.currency_id
        prec = company_currency.decimal_places
        amount = current_currency._convert(
            self.amount, company_currency, self.asset_id.company_id, depreciation_date)
        asset_name = self.asset_id.name + ' (%s/%s)' % (self.sequence, len(self.asset_id.depreciation_line_ids))
        move_line_1 = {
            'name': asset_name,
            'account_id': category_id.depreciation_account_id.id,
            'debit': 0.0 if float_compare(amount, 0.0, precision_digits=prec) > 0 else -amount,
            'credit': amount if float_compare(amount, 0.0, precision_digits=prec) > 0 else 0.0,
            'partner_id': self.asset_id.partner_id.id,
            'analytic_account_id': analytic_account_id.id if category_id.type == 'sale' else False,
            'analytic_tag_ids': [(6, 0, analytic_tag_ids.ids)] if category_id.type == 'sale' else False,
            'currency_id': company_currency != current_currency and current_currency.id or False,
            'amount_currency': company_currency != current_currency and -1.0 * self.amount or 0.0,
        }

        if self.disposal and category_id.disposal_expense_account_id:
            account_id = self.asset_id.category_id.disposal_expense_account_id
        else:
            account_id = self.asset_id.depreciation_expense_account_id or category_id.depreciation_expense_account_id

        move_line_2 = {
            'name': asset_name,
            'account_id': account_id.id,
            'credit': 0.0 if float_compare(amount, 0.0, precision_digits=prec) > 0 else -amount,
            'debit': amount if float_compare(amount, 0.0, precision_digits=prec) > 0 else 0.0,
            'partner_id': self.asset_id.partner_id.id,
            'analytic_account_id': analytic_account_id.id if category_id.type == 'purchase' else False,
            'analytic_tag_ids': [(6, 0, analytic_tag_ids.ids)] if category_id.type == 'purchase' else False,
            'currency_id': company_currency != current_currency and current_currency.id or False,
            'amount_currency': company_currency != current_currency and self.amount or 0.0,
        }
        move_vals = {
            'ref': self.asset_id.code,
            'date': depreciation_date or False,
            'journal_id': category_id.journal_id.id,
            'line_ids': [(0, 0, move_line_1), (0, 0, move_line_2)],
            'auto_post': False if self.asset_id.state == 'draft' else True,
        }
        return move_vals

    def post_lines_and_close_asset(self):
        # we re-evaluate the assets to determine whether we can close them and create disposed journal entry for asset
        for line in self:
            line.log_message_when_posted()
        for asset in self.asset_id:
            if not asset.depreciation_line_ids.filtered(lambda line: line.move_id.state == 'draft') \
                and asset.currency_id.is_zero(asset.value_residual):
                asset.create_account_move()

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
            if line.move_id.state == 'posted':
                partner_name = line.asset_id.partner_id.name
                currency_name = line.asset_id.currency_id.name
                msg_values = {_('Currency'): currency_name, _('Amount'): line.amount}
                if partner_name:
                    msg_values[_('Partner')] = partner_name
                msg = _format_message(_('Depreciation line posted.'), msg_values)
                line.asset_id.message_post(body=msg)

    def unlink(self):
        for record in self:
            if record.move_check and (record.move_id.state == 'posted' or (record.move_id.name != '/' and not self.env.context.get('force_delete', False))):
                if record.asset_id.category_id.type == 'purchase':
                    msg = _("You cannot delete posted depreciation lines.")
                else:
                    msg = _("You cannot delete posted installment lines.")
                raise UserError(msg)
        return super(AccountAssetDepreciationLine, self).unlink()
