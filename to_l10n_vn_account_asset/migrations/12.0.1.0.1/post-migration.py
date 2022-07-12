from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    prepaid_expense_tags = env.ref('l10n_vn_c200.analytic_tag_short_term_prepaid_expense') | env.ref('l10n_vn_c200.analytic_tag_long_term_prepaid_expense')
    
    categories = env['account.asset.category'].search([]).filtered(
        lambda c: c.account_depreciation_id.code.startswith('242') \
                  or (c.account_revaluation_decrease_asset_id and c.account_revaluation_decrease_asset_id.code.startswith('242')) \
                  or (c.account_revaluation_increase_asset_id and c.account_revaluation_increase_asset_id.code.startswith('242')))
    assets = env['account.asset.asset'].search([('category_id', 'in', categories.ids)])
    for a in assets:
        for move in (a.depreciation_line_ids.mapped('move_id') | a.revaluation_line_ids.mapped('move_id')):
            for line in move.line_ids:
                 if line.account_id.code.startswith('242'):
                    prepaid_tags = a.analytic_tag_ids.filtered(lambda t: t in prepaid_expense_tags)
                    line.write({
                        'analytic_tag_ids': [(6, 0, (line.analytic_tag_ids | prepaid_tags).ids)],
                        })
