# -*- coding: utf-8 -*-

from odoo import models, _


class AccountJournal(models.Model):
    _inherit = 'account.journal'

    def _get_bank_statements_available_import_formats(self):
        """ Returns a list of strings representing the supported import formats.
        """
        return ['*.csv', '*.xlsx']

    def __get_bank_statements_available_sources(self):
        rslt = super(AccountJournal, self).__get_bank_statements_available_sources()
        formats_list = self._get_bank_statements_available_import_formats()
        if formats_list:
            formats_list.sort()
            import_formats_str = ', '.join(formats_list)
            rslt.append(("file_import", _("Import [%s]") % import_formats_str))
        return rslt

    def import_statement(self):
        """return action to import bank/cash statements. This button should be called only on journals with type =='bank'"""
        action_name = 'action_viin_account_bank_statement_import'
        action = self.env['ir.actions.act_window']._for_xml_id('viin_account_bank_statement_import.%s' % action_name)
        # Note: this drops action['context'], which is a dict stored as a string, which is not easy to update
        action.update({'context': (u"{'journal_id': " + str(self.id) + u"}")})
        return action
