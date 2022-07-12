from odoo import models, fields, _
from odoo.exceptions import ValidationError
from odoo.tools import format_date


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    forward_aml_id = fields.Many2one('account.move.line', string='Forward Journal Item', readonly=True, copy=False,
                                     help="The technical field that stores the journal item which holds the balance"
                                     " carried from this journal item")
    forwarded_from_aml_ids = fields.One2many('account.move.line', 'forward_aml_id', string='Closing for', readonly=True,
                                             help="The technical field that stores all the journal items whose balance"
                                             " is carried forward this journal item")

    forward_line_id = fields.Many2one('balance.carry.forward.rule.line', string='Balance Forward Line', index=True, readonly=True, copy=False)
    balance_carry_forward_id = fields.Many2one('balance.carry.forward', string='Balance Forward Document',
                                       related='forward_line_id.forward_id', store=True, index=True, copy=False)
    forward_rule_id = fields.Many2one('balance.carry.forward.rule', string='Balance Carry Forward Rule', related='forward_line_id.rule_id',
                                      store=True, copy=False,
                                      help="The Balance Carry Forward Rule that created this journal item")

    def _prepare_balance_carry_forward_move_data(self, journal, dest_account, date):
        if len(self.mapped('account_id')) > 1:
            raise ValidationError(_("Programming error in the method `_prepare_balance_carry_forward_move_data`."))

        account = self[0].account_id
        latest_line = self.sorted('date', reverse=False)[0]
        if date < latest_line.date:
            raise ValidationError(_("You must specify a date which is later than or equal to %s, which is the date of the latest journal item %s.")
                                  % (format_date(self.env, latest_line.date), latest_line.display_name))
        balance = sum(self.mapped('balance'))
        line1 = {
            'name': _("Closing Account: %s") % account.code,
            'account_id': account.id,
            'debit': 0.0 if balance > 0.0 else -balance,
            'credit': 0.0 if balance < 0.0 else balance,
            'company_id': account.company_id.id,
            }
        line2 = {
            'name': _("Closing Account: %s") % account.code,
            'account_id': dest_account.id,
            'debit': 0.0 if balance < 0.0 else balance,
            'credit': 0.0 if balance > 0.0 else -balance,
            'company_id': account.company_id.id,
            }
        return {
            'journal_id': journal.id,
            'ref': _("Forward balance from %s to %s") % (account.code, dest_account.code),
            'date': date,
            'company_id': account.company_id.id,
            # ensure debit line first
            'line_ids': [(0, 0, line1), (0, 0, line2)] if balance < 0.0 else [(0, 0, line2), (0, 0, line1)],
            }

    def carry_balance_forward(self, journal, dest_account, date):
        moves = self.env['account.move']
        for account in self.mapped('account_id'):
            source_move_lines = self.filtered(lambda l: l.account_id == account)
            moves += moves.create(source_move_lines._prepare_balance_carry_forward_move_data(journal, dest_account, date))
        return moves

    def action_carry_balance_forward_entry(self):
        action = self.env["ir.actions.act_window"]._for_xml_id('to_account_balance_carry_forward.account_balance_carry_forward_wizard_action')
        action['context'] = self.env.context
        return action

    def write(self, vals):
        if 'debit' in vals or 'credit' in vals:
            for move in self.filtered(lambda l: l.forward_aml_id).mapped('move_id'):
                links = []
                for forward_move in move.line_ids.mapped('forward_aml_id.move_id'):
                    links.append(
                        '<a href=# data-oe-model=account.move data-oe-id={id}>{name}</a>'.format(
                            id=forward_move.id,
                            name=forward_move.name
                            )
                        )
                if links:
                    move.message_post(
                        body=_("Because either debit or credit has been modified, the following journal entries"
                               " should be updated accordingly since they are balance carry forward entries for"
                               " the current entry.<br />%s") % ', '.join(links)
                        )
        return super(AccountMoveLine, self).write(vals)

