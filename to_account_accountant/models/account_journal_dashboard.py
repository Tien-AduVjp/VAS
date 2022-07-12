from odoo import models


class AccountJournalDashboard(models.Model):
    _inherit = 'account.journal'

    def open_action(self):
        action = super(AccountJournalDashboard, self).open_action()
        ctx = action.get('context', {})
        # remove misc and manual filter
        if ctx.get('default_move_type') == 'entry':
            if 'search_default_misc_filter' in ctx and ctx['search_default_misc_filter']:
                ctx['search_default_misc_filter'] = 0
            if 'search_default_manual_entry' in ctx and ctx['search_default_manual_entry']:
                ctx['search_default_manual_entry'] = 0
            action['context'].update(ctx)
        return action
