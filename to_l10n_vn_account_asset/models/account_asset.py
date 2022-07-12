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
