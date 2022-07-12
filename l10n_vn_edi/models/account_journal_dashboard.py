from odoo import models, fields


class AccountJournal(models.Model):
    _inherit = "account.journal"

    def _get_einvoices_to_issue_domain(self):
        '''
        Hook method for potential inheritance
        '''
        domain = [
            ('state', '!=', 'cancel'),
            ('move_type', '=', 'out_invoice'),
            ('einvoice_state', '=', 'not_issued'),
            ('invoice_date', '<=', fields.Date.context_today(self)),
            ('journal_id', '=', self.id), ]
        if self.account_einvoice_serial_id.einvoice_service_id.start_date:
            domain.append(('invoice_date', '>', self.account_einvoice_serial_id.einvoice_service_id.start_date))
        return domain

    def _get_einvoices_to_issue(self):
        return self.env['account.move'].search(self._get_einvoices_to_issue_domain())

    def get_journal_dashboard_datas(self):
        action = super(AccountJournal, self).get_journal_dashboard_datas()
        einvoice_to_issue = self._get_einvoices_to_issue()
        action.update({
            'einvoice_to_issue_count': len(einvoice_to_issue),
            'einvoice_enabled': self.einvoice_enabled,
            })
        return action

    def action_open_einvoice_to_issue_action(self):
        self.ensure_one()
        result = self.env["ir.actions.act_window"]._for_xml_id('account.action_move_out_invoice_type')

        # reset context
        result['context'] = {}
        # choose the view_mode accordingly
        einvoice_to_issue = self._get_einvoices_to_issue()
        einvoice_to_issue_count = len(einvoice_to_issue)
        if einvoice_to_issue_count != 1:
            result['domain'] = self._get_einvoices_to_issue_domain()
        elif einvoice_to_issue_count == 1:
            res = self.env.ref('account.view_move_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = einvoice_to_issue.id
        return result

