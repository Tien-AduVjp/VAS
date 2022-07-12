# -*- coding: utf-8 -*-

import logging

from odoo import fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.addons.base.models.res_bank import sanitize_account_number

_logger = logging.getLogger(__name__)


class AccountBankStatementImport(models.TransientModel):
    _name = 'account.bank.statement.import'
    _description = 'Import Bank Statement'

    attachment_ids = fields.Many2many('ir.attachment', string='Files', required=True,
                                      help='Get you bank statements in electronic format from your bank and'
                                           ' select them here.')

    def import_file(self):
        """ Process the file chosen in the wizard, create bank statement(s) and go to reconciliation. """
        self.ensure_one()
        all_statements = self.env['account.bank.statement']
        statement_line_ids_all = []
        notifications_all = []
        # Let the appropriate implementation module parse the file and return the required data
        # The active_id is passed in context in case an implementation module requires information about the wizard state (see QIF)
        for attachment in self.attachment_ids:
            currency_code, account_number, stmts_vals = attachment.with_context(active_id=self.ids[0])._parse_as_bank_statement()
            # Check raw data
            self._check_parsed_data(stmts_vals, account_number)
            # Try to find the currency and journal in odoo
            currency, journal = self._find_additional_data(currency_code, account_number)
            # If no journal found, ask the user about creating one
            if not journal:
                # The active_id is passed in context so the wizard can call import_file again once the journal is created
                return self.with_context(active_id=self.ids[0])._journal_creation_wizard(currency, account_number)
            if not journal.payment_debit_account_id or not journal.payment_credit_account_id:
                raise UserError(_('You have to set a Outstanding Receipts Account and a Outstanding Payments Account for the journal: %s')
                                % (journal.name,))
            # Prepare statement data to be used for bank statements creation
            stmts_vals = self._complete_stmts_vals(stmts_vals, journal, account_number)
            # Create the bank statements
            statements, statement_line_ids, notifications = self._create_bank_statements(stmts_vals)
            all_statements |= statements
            statement_line_ids_all.extend(statement_line_ids)
            notifications_all.extend(notifications)
            # Now that the import worked out, set it as the bank_statements_source of the journal
            if journal.bank_statements_source != 'file_import':
                # Use sudo() because only 'account.group_account_manager'
                # has write access on 'account.journal', but 'account.group_account_user'
                # must be able to import bank statement files
                journal.sudo().bank_statements_source = 'file_import'

        # if all lines having their partner specified, dispatch to reconciliation interface
        if all_statements.line_ids and all(line.partner_id for line in all_statements.line_ids):
            all_statements.button_post()
            action = {
                'type': 'ir.actions.client',
                'tag': 'bank_statement_reconciliation_view',
                'context': {
                    'statement_line_ids': statement_line_ids_all,
                    'company_ids': all_statements.company_id.ids or self.env.user.company_ids.ids,
                    'notifications': notifications_all,
                    },
                }
        # redirect to either statement tree view or form view
        else:
            stm_count = len(all_statements)
            action = self.env['ir.actions.act_window']._for_xml_id('account.action_bank_statement_tree')
            # override the context to get rid of the default filtering
            action['context'] = {}
            if stm_count != 1:
                action['domain'] = "[('id', 'in', %s)]" % str(all_statements.ids)
            else:
                res = self.env.ref('account.view_bank_statement_form', False)
                action['views'] = [(res and res.id or False, 'form')]
                action['res_id'] = all_statements.id
        return action

    def _journal_creation_wizard(self, currency, account_number):
        """ Calls a wizard that allows the user to carry on with journal creation """
        return {
            'name': _('Journal Creation'),
            'type': 'ir.actions.act_window',
            'res_model': 'account.bank.statement.import.journal.creation',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'statement_import_transient_id': self.env.context['active_id'],
                'default_bank_acc_number': account_number,
                'default_name': _('Bank') + ' ' + account_number,
                'default_currency_id': currency and currency.id or False,
                'default_type': 'bank',
            }
        }

    def _check_parsed_data(self, stmts_vals, account_number):
        """ Basic and structural verifications """
        extra_msg = _('If it contains transactions for more than one account, it must be imported on each of them.')
        if len(stmts_vals) == 0:
            raise UserError(
                _("This file doesn't contain any statement for account %s.") % (account_number,)
                +'\n' + extra_msg
            )

        no_st_line = True
        for vals in stmts_vals:
            if vals['transactions'] and len(vals['transactions']) > 0:
                no_st_line = False
                break
        if no_st_line:
            raise UserError(
                _("This file doesn't contain any transaction for account %s.") % (account_number,)
                +'\n' + extra_msg
            )

    def _check_journal_bank_account(self, journal, account_number):
        # Needed for CH to accommodate for non-unique account numbers
        sanitized_acc_number = journal.bank_account_id.sanitized_acc_number
        if " " in sanitized_acc_number:
            sanitized_acc_number = sanitized_acc_number.split(" ")[0]
        return sanitized_acc_number == account_number

    def _find_additional_data(self, currency_code, account_number):
        """ Look for a res.currency and account.journal using values extracted from the
            statement and make sure it's consistent.
        """
        company_currency = self.env.company.currency_id
        journal_obj = self.env['account.journal']
        currency = None
        sanitized_account_number = sanitize_account_number(account_number)

        if currency_code:
            if isinstance(currency_code, list):
                if len(currency_code) > 1:
                    raise ValidationError(_("There are more than one currency which is not supported."))
                else:
                    currency_code = currency_code[0]
            currency = self.env['res.currency'].search([('name', '=ilike', currency_code)], limit=1)
            if not currency:
                raise UserError(_("No currency found matching '%s'.") % currency_code)
            if currency == company_currency:
                currency = False

        journal = journal_obj.browse(self.env.context.get('journal_id', []))
        if account_number:
            # No bank account on the journal : create one from the account number of the statement
            if journal and not journal.bank_account_id:
                journal.set_bank_account(account_number)
            # No journal passed to the wizard : try to find one using the account number of the statement
            elif not journal:
                journal = journal_obj.search([('bank_account_id.sanitized_acc_number', '=', sanitized_account_number)])
            # Already a bank account on the journal : check it's the same as on the statement
            else:
                if not self._check_journal_bank_account(journal, sanitized_account_number):
                    raise UserError(_('The account of this statement (%s) is not the same as the journal (%s).') % (account_number, journal.bank_account_id.acc_number))

        # If importing into an existing journal, its currency must be the same as the bank statement
        if journal:
            journal_currency = journal.currency_id
            if currency is None:
                currency = journal_currency
            if currency and currency != journal_currency:
                statement_cur_code = not currency and company_currency.name or currency.name
                journal_cur_code = not journal_currency and company_currency.name or journal_currency.name
                raise UserError(_('The currency of the bank statement (%s) is not the same as the currency of the journal (%s).') % (statement_cur_code, journal_cur_code))

        # If we couldn't find / can't create a journal, everything is lost
        if not journal and not account_number:
            raise UserError(_('Cannot find in which journal import this statement. Please manually select a journal.'))

        return currency, journal

    def _complete_stmts_vals(self, stmts_vals, journal, account_number):
        for st_vals in stmts_vals:
            st_vals['journal_id'] = journal.id
            if not st_vals.get('reference'):
                st_vals['reference'] = " ".join(self.attachment_ids.mapped('name'))
            if st_vals.get('number'):
                # build the full name like BNK/2016/00135 by just giving the number '135'
                st_vals['name'] = journal.sequence_id.with_context(ir_sequence_date=st_vals.get('date')).get_next_char(st_vals['number'])
                del(st_vals['number'])
            for line_vals in st_vals['transactions']:
                unique_import_id = line_vals.get('unique_import_id')
                if unique_import_id:
                    sanitized_account_number = sanitize_account_number(account_number)
                    line_vals['unique_import_id'] = (sanitized_account_number and sanitized_account_number + '-' or '') + str(journal.id) + '-' + unique_import_id

                if not line_vals.get('partner_bank_id'):
                    # Find the partner and his bank account or create the bank account. The partner selected during the
                    # reconciliation process will be linked to the bank when the statement is closed.
                    identifying_string = line_vals.get('account_number')
                    if identifying_string:
                        partner_bank = self.env['res.partner.bank'].search([('acc_number', '=', identifying_string)], limit=1)
                        if partner_bank:
                            line_vals['partner_bank_id'] = partner_bank.id
                            line_vals['partner_id'] = partner_bank.partner_id.id
                if not line_vals.get('partner_id', False) and line_vals.get('partner_name', False):
                    partner = self.env['res.partner'].search([('name', '=', line_vals['partner_name'])], limit=1)
                    if not partner:
                        partner = self.env['res.partner'].search([('name', '=ilike', line_vals['partner_name'])], limit=1)
                    if partner:
                        line_vals['partner_id'] = partner.id
                if 'currency' in line_vals:
                    del line_vals['currency']
        return stmts_vals

    def _create_bank_statements(self, stmts_vals):
        """ Create new bank statements from imported values, filtering out already imported transactions, and returns data used by the reconciliation widget """
        statements = self.env['account.bank.statement']
        BankStatementLine = self.env['account.bank.statement.line']

        vals_list = []
        # Filter out already imported transactions and create statements
        statement_line_ids = []
        ignored_statement_lines_import_ids = []
        for st_vals in stmts_vals:
            filtered_st_lines = []
            for line_vals in st_vals['transactions']:
                if 'unique_import_id' not in line_vals \
                   or not line_vals['unique_import_id'] \
                   or not bool(BankStatementLine.sudo().search([('unique_import_id', '=', line_vals['unique_import_id'])], limit=1)):
                    filtered_st_lines.append(line_vals)
                else:
                    ignored_statement_lines_import_ids.append(line_vals['unique_import_id'])
                    if 'balance_start' in st_vals:
                        st_vals['balance_start'] += float(line_vals['amount'])

            if len(filtered_st_lines) > 0:
                # Remove values that won't be used to create records
                st_vals.pop('transactions', None)
                # Create the statement
                st_vals['line_ids'] = [[0, False, line] for line in filtered_st_lines]
                vals_list.append(st_vals)
        if vals_list:
            statements = statements.create(vals_list)
            statement_line_ids.extend(statements.line_ids.ids)
        if len(statement_line_ids) == 0:
            raise UserError(_('You already have imported that file.'))

        # Prepare import feedback
        notifications = []
        num_ignored = len(ignored_statement_lines_import_ids)
        if num_ignored > 0:
            notifications += [{
                'type': 'warning',
                'message': _("%d transactions had already been imported and were ignored.") % num_ignored if num_ignored > 1 else _("1 transaction had already been imported and was ignored."),
                'details': {
                    'name': _('Already imported items'),
                    'model': 'account.bank.statement.line',
                    'ids': BankStatementLine.search([('unique_import_id', 'in', ignored_statement_lines_import_ids)]).ids
                }
            }]
        return statements, statement_line_ids, notifications
