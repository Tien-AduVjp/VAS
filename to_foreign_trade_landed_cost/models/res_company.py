from odoo import models, fields, _


class ResCompany(models.Model):
    _inherit = "res.company"
    
    landed_cost_journal_id = fields.Many2one('account.journal', string='Landed Cost Journal')
    
    
    def create_landed_cost_journal_if_not_exists(self):
        self.ensure_one()
        Journal = self.env['account.journal']
        journal_id = Journal.search([('code', '=', 'ITLC'), ('company_id', '=', self.id)])
        if not journal_id:
            journal_id = Journal.create(self._prepare_landed_cost_journal_data())
        self.write({'landed_cost_journal_id': journal_id.id})
        return journal_id

    def _prepare_landed_cost_journal_data(self):
        return {
            'name': _('Default Landed Cost Journal'),
            'code': 'ITLC',
            'type': 'general',
            'company_id': self.id,
            'show_on_dashboard': False,
            }

