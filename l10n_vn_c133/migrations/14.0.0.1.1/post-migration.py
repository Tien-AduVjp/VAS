from odoo import api, SUPERUSER_ID


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    account_type_expenses = env.ref('account.data_account_type_expenses')
    companies = env['res.company'].search([('chart_template_id', '=', env.ref('l10n_vn_c133.vn_template_c133').id)])
    accounts_611 = env['account.account'].search([
        ('company_id', 'in', companies.ids),
        ('code', '=ilike', '611' + '%'),
        ('user_type_id', '!=', account_type_expenses.id),
    ])
    if accounts_611:
        accounts_611.write({'user_type_id': account_type_expenses.id})
