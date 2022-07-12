from odoo import api, fields, models


class AccountAssetRevaluationLine(models.Model):
    _inherit = 'account.asset.revaluation.line'

    day = fields.Char(string='Day', compute='_compute_date')
    month = fields.Char(string='Month', compute='_compute_date')
    year = fields.Char(string='Year', compute='_compute_date')

    @api.depends('revaluation_date')
    def _compute_date(self):
        for r in self:
            if not r.revaluation_date:
                r.day = False
                r.month = False
                r.year = False
            else:
                year, month, day = self.env['to.base'].split_date(r.revaluation_date)
                r.day = day > 9 and str(day) or '0' + str(day)
                r.month = month > 9 and str(month) or '0' + str(month)
                r.year = str(year)

    def _prepare_move(self):
        self.ensure_one()
        res = super(AccountAssetRevaluationLine, self)._prepare_move()

        revaluation_increase_account = self.asset_id.revaluation_increase_account_id or self.asset_id.category_id.revaluation_increase_account_id
        revaluation_decrease_account = self.asset_id.revaluation_decrease_account_id or self.asset_id.category_id.revaluation_decrease_account_id
        if (revaluation_increase_account and revaluation_increase_account.code.startswith('242'))\
           or (revaluation_decrease_account and revaluation_decrease_account.code.startswith('242')):
            analytic_tag_ids = self.asset_id.analytic_tag_ids

            prepaid_expense_tags = self.env.ref('l10n_vn_common.account_analytic_tag_short_term_prepaid_expense') | self.env.ref('l10n_vn_common.account_analytic_tag_long_term_prepaid_expense')
            prepaid_expense_tags = analytic_tag_ids.filtered(lambda t: t in prepaid_expense_tags)

            line_ids = res['line_ids']
            Tag = self.env['account.analytic.tag']
            # move_line_1
            analytic_tag_ids = line_ids[0][2]['analytic_tag_ids'] and Tag.browse(line_ids[0][2]['analytic_tag_ids'][0][2]) or Tag
            line_ids[0][2].update({
                'analytic_tag_ids': [(6, 0, (analytic_tag_ids | prepaid_expense_tags).ids)],
            })

            # move_line_2
            analytic_tag_ids = line_ids[1][2]['analytic_tag_ids'] and Tag.browse(line_ids[1][2]['analytic_tag_ids'][0][2]) or Tag
            line_ids[1][2].update({
                'analytic_tag_ids': [(6, 0, (analytic_tag_ids | prepaid_expense_tags).ids)],
            })
        return res
