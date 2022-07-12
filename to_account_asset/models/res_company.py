from odoo import models, _


class ResCompany(models.Model):
    _inherit = 'res.company'

    def _prepare_asset_journal_data(self):
        self.ensure_one()
        return {
            'name': _('Assets'),
            'type': 'general',
            'code': 'ASSET',
            'show_on_dashboard': False,
            'sequence': 12,
            'company_id': self.id,
            }

    def _generate_asset_journal(self):
        vals_list = []
        # only generate asset journal for companies having a chart of account installed
        for r in self.filtered(lambda c: c.chart_template_id):
            # only generate if not exists
            if not self.env['account.journal'].search([('code', '=', 'ASSET'), ('company_id', '=', r.id)]):
                vals_list.append(r._prepare_asset_journal_data())
        return self.env['account.journal'].create(vals_list)
