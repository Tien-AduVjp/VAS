from odoo import models


class AccountReport(models.AbstractModel):
    _inherit = 'account.report'
    _description = 'Accounting Report'

    filter_show_ignored_entries = None

    def set_context(self, options):
        """This method will set information inside the context based on the options dict as some options need to be in context for the query_get method defined in account_move_line"""
        ctx = super(AccountReport, self).set_context(options)
        if options.get('show_ignored_entries') is not None:
            ctx['ignored'] = options.get('show_ignored_entries') and 'show_ignored' or 'hide_ignored'
        return ctx
