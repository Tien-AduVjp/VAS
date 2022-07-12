from odoo import api, fields, models


class AccountAssetAsset(models.Model):
    _inherit = 'account.asset.asset'

    day = fields.Char(string='Day', compute='_compute_date', store=True)
    month = fields.Char(string='Month', compute='_compute_date', store=True)
    year = fields.Char(string='Year', compute='_compute_date', store=True)

    @api.depends('date')
    def _compute_date(self):
        for r in self:
            if not r.date:
                r.day = False
                r.month = False
                r.year = False
            else:
                year, month, day = self.env['to.base'].split_date(r.date)
                r.day = day > 9 and str(day) or '0' + str(day)
                r.month = month > 9 and str(month) or '0' + str(month)
                r.year = str(year)

    def action_view_sales_invoice(self):
        res = super(AccountAssetAsset, self).action_view_sales_invoice()

        move_ids = self.move_ids.filtered(lambda move: move.move_type == 'out_invoice')
        # choose the view_mode accordingly
        if len(move_ids) <= 1:
            vn_charts = self.env['account.chart.template']._get_installed_vietnam_coa_templates()
            if self.company_id.chart_template_id.id in vn_charts.ids:
                account_711 = self.env['account.account'].search([
                    ('code', '=', '711'),
                    ('company_id', '=', self.company_id.id)], limit=1)
                if account_711:
                    res['context']['default_line_ids'][0][2].update({
                            'account_id': account_711.id,
                        })
        return res
