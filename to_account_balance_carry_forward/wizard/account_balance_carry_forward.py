from odoo import api, fields, models, _
from odoo.exceptions import UserError


class AccountBalanceCarryForwardWizard(models.TransientModel):
    _name = 'account.balance.carry.forward.wizard'
    _description = 'Carry Balance Forward'

    date = fields.Date(required=True)
    company_id = fields.Many2one('res.company', required=True)
    active_move_line_ids = fields.Many2many('account.move.line')
    journal_id = fields.Many2one('account.journal', required=True,
        domain="[('company_id', '=', company_id), ('type', '=', 'general')]")
    dest_account_id = fields.Many2one('account.account', string='Destination Account', required=True, domain="[('company_id', '=', company_id)]")
    total_amount = fields.Monetary(compute="_compute_total_amount", currency_field='company_currency_id')
    company_currency_id = fields.Many2one('res.currency', related='company_id.currency_id')

    @api.depends('active_move_line_ids')
    def _compute_total_amount(self):
        for r in self:
            r.total_amount = sum(r.active_move_line_ids.mapped('balance'))

    @api.constrains('active_move_line_ids', 'dest_account_id')
    def _check_accounts(self):
        for r in self:
            if r.dest_account_id.id in r.active_move_line_ids.mapped('account_id').ids:
                raise UserError(_("You cannot forward balance to the same account. Please select another destination account"
                                  " or deselect journal items of the account %s") % r.dest_account_id.display_name)

    @api.model
    def default_get(self, fields):
        if self.env.context.get('active_model') != 'account.move.line' or not self.env.context.get('active_ids'):
            raise UserError(_('Balance Carry Forward can only be used on journal items'))
        rec = super(AccountBalanceCarryForwardWizard, self).default_get(fields)
        active_move_line_ids = self.env['account.move.line'].browse(self.env.context['active_ids'])
        rec['active_move_line_ids'] = active_move_line_ids.ids

        if any(move.state != 'posted' for move in active_move_line_ids.mapped('move_id')):
            raise UserError(_('You can only forward the balance for posted journal items.'))
        if any(move_line.forward_aml_id for move_line in active_move_line_ids):
            raise UserError(_('You can only forward the balance for items the balance of which are not yet forwarded.'))

        if any(line.company_id != active_move_line_ids[0].company_id for line in active_move_line_ids):
            raise UserError(_('All lines must be from the same company.'))
        company_id = active_move_line_ids[0].company_id
        rec['company_id'] = company_id.id
        rec['journal_id'] = company_id.balance_carry_forward_journal_id.id
        return rec

    def amend_entries(self):
        moves = self.active_move_line_ids.carry_balance_forward(self.journal_id, self.dest_account_id, self.date)

        # open the generated entries
        action = {
            'name': _('Generated Entries'),
            'domain': [('id', 'in', moves.ids)],
            'res_model': 'account.move',
            'view_mode': 'tree,form',
            'type': 'ir.actions.act_window',
            'views': [(self.env.ref('account.view_move_tree').id, 'tree'), (False, 'form')],
        }
        if len(moves) == 1:
            action.update({'view_mode': 'form', 'res_id': moves.id})
        return action
