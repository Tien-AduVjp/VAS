from odoo import api, fields, models


class AccountAssetDepreciationLine(models.Model):
    _inherit = 'account.asset.depreciation.line'

    day = fields.Char(string='Day', compute='_compute_date')
    month = fields.Char(string='Month', compute='_compute_date')
    year = fields.Char(string='Year', compute='_compute_date')

    @api.depends('depreciation_date')
    def _compute_date(self):
        for r in self:
            if not r.depreciation_date:
                r.day = False
                r.month = False
                r.year = False
            else:
                year, month, day = self.env['to.base'].split_date(r.depreciation_date)
                r.day = day > 9 and str(day) or '0' + str(day)
                r.month = month > 9 and str(month) or '0' + str(month)
                r.year = str(year)

    def _prepare_move(self):
        res = super(AccountAssetDepreciationLine, self)._prepare_move()

        category_id = self.asset_id.category_id
        if category_id.depreciation_account_id.code.startswith('242'):
            analytic_tag_ids = self.asset_id.analytic_tag_ids
            prepaid_expense_tags = self.env.ref('l10n_vn_c200.analytic_tag_short_term_prepaid_expense') | self.env.ref('l10n_vn_c200.analytic_tag_long_term_prepaid_expense')
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

    def _prepare_move_grouped(self):
        res = super(AccountAssetDepreciationLine, self)._prepare_move_grouped()

        asset_id = self[0].asset_id
        category_id = asset_id.category_id  # we can suppose that all lines have the same category
        if category_id.depreciation_account_id.code.startswith('242'):
            analytic_tag_ids = asset_id.analytic_tag_ids
            prepaid_expense_tags = self.env.ref('l10n_vn_c200.analytic_tag_short_term_prepaid_expense') | self.env.ref('l10n_vn_c200.analytic_tag_long_term_prepaid_expense')
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
