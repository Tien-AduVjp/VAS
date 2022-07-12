import logging

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class BalanceCarryForwardRule(models.Model):
    _name = 'balance.carry.forward.rule'
    _description = 'Balance Carry Forward Rule'
    _order = 'succeeding_rule_id, sequence'

    name = fields.Char(string='Entry Name', required=True, translate=True)
    sequence = fields.Integer(string='Sequence')
    forward_type = fields.Selection(
        [('auto', 'Auto'),
         ('cr_db', 'Credit -> Debit'),
         ('db_cr', 'Debit -> Credit')], string='Forward Method', required=True, default='auto',
        help="The balance of an account is computed by debit sum - credit sum (of all the journal items) of an account.\n"
        "Auto: If the balance of the Source Account is greater than zero, a new journal item will be created to"
        " DEBIT the balance into the Destimation Account and CREDIT the same amount into the Source Account. If the balance"
        " is less than zero, the entry will be reversed.\n"
        "Credit -> Debit: CREDIT the Destimation Account and DEBIT the Source Account with the Credit Balance of the source"
        " account. If the source account has Debit Balance instead, an exception will be raised.\n"
        "Debit -> Credit: The reverse way of the method 'Credit -> Debit'.\n"
        "In general, 'Auto' is the most suitable method for account that may have positive balance a time and negative one another time."
        " 'Credit -> Debit' is the method to ensure that the SOURCE account must have NEGATIVE balance to be able to get carried forward."
        " 'Debit -> Credit' is the method to ensure that the SOURCE account must have POSITIVE balance to be able to get carried forward.\n"
        "If you are not sure about these, please choose 'Auto'.")

    source_account_type_categ_id = fields.Many2one('account.account.type', string='Source Account Type',
                                                   help="The source account type of which the accounts' balance will be carried forward to the Destination Account.")

    source_account_ids = fields.Many2many('account.account', string='Source Accounts', required=True, compute='_compute_source_accounts', store=True,
                                        readonly=False, help="The source account from which the balance will be carried forward.")
    dest_account_id = fields.Many2one('account.account', string='Destination Account', required=True,
                                         help="The destination account to which the balance of the Source Account will be carried forward.")
    profit_loss = fields.Boolean(string='Profit/Loss')
    succeeding_rule_id = fields.Many2one('balance.carry.forward.rule', string='Succeeding Rule', ondelete='restrict', auto_join=True,
                                      help="The rule that requires result from this rule")

    preceding_rule_ids = fields.One2many('balance.carry.forward.rule', 'succeeding_rule_id', string='Preceding Rules',
                                      help="The rules required to be excecuted and done before executing this rule")

    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.company, required=True,
                                 help="Leave this empty so that the rule is applicable to all the available companies.")

    @api.constrains('source_account_ids', 'dest_account_id', 'company_id')
    def _check_company(self):
        for r in self:
            if r.dest_account_id.company_id.id not in r.source_account_ids.mapped('company_id').ids or r.dest_account_id.company_id != r.company_id:
                raise ValidationError(_("You cannot forward balance for accounts in different companies"))

    @api.constrains('source_account_ids', 'dest_account_id')
    def _check_accounts(self):
        for r in self:
            if r.dest_account_id.id in r.source_account_ids.ids:
                raise ValidationError(_("You can not forward the balance to the same account %s")
                                          % (r.dest_account_id.code,))
            overlap = self.search([
                ('id', '!=', r.id),
                ('company_id', '=', r.company_id.id),
                ('source_account_ids', 'in', r.source_account_ids.ids)], limit=1)
            if overlap:
                overlapped_acc = False
                for acc in r.source_account_ids:
                    if acc.id in overlap.source_account_ids.ids:
                        overlapped_acc = acc
                raise ValidationError(_("You've tried to create a new rule that overlaps an exiting rule '%s' on source accounts."
                                        " The overlapped account is '%s'")
                                      % (overlap.name, overlapped_acc.code))

    @api.depends('source_account_type_categ_id')
    def _compute_source_accounts(self):
        for r in self:
            if r.source_account_type_categ_id:
                r.source_account_ids = r.env['account.account'].search([
                    ('user_type_id', '=', r.source_account_type_categ_id.id),
                    ('company_id', '=', r.company_id.id)
                    ])
            else:
                r.source_account_ids = False
    
    def _prepare_rule_line_vals(self, source_aml_ids, source_account_id):
        """
        :param source_aml_ids: list of integer
        :param source_account_id: integer
        """
        self.ensure_one()
        return {
            'rule_id': self.id,
            'sequence': self.sequence,
            'source_account_id': source_account_id,
            'dest_account_id': self.dest_account_id.id,
            'forward_type': self.forward_type,
            'source_aml_ids': source_aml_ids and [(6, 0, source_aml_ids)] or [(5, 0, 0)],
            }

    def _prepare_rule_line_data(self, source_account, date=None):
        # TODO: remove me in 15/master
        _logger.warning("The method `_prepare_rule_line_data() is deprecated and will be removed soon."
                        " Please use the `_prepare_rule_line_vals()` instead.")
        date = date or fields.Date.today()
        source_aml_ids = self.env['account.move.line'].search([
            ('account_id', '=', source_account.id),
            ('date', '<=', date),
            ('parent_state', '=', 'posted'),
            ('forward_aml_id', '=', False),
            ('forwarded_from_aml_ids', '=', False)
            ])
        return self._prepare_rule_line_vals(source_aml_ids.ids, source_account.id)

