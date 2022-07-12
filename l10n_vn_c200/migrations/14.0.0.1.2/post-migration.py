from odoo import api, SUPERUSER_ID


def _update_account_user_type_c200(env):
    account_type_current_assets = env.ref('account.data_account_type_current_assets')
    account_type_current_liabilities = env.ref('account.data_account_type_current_liabilities')
    companies = env['res.company'].search([('chart_template_id', '=', env.ref('l10n_vn.vn_template').id)])
    accounts_update_to_current_assets = env['account.account'].search([
        ('company_id', 'in', companies.ids),
        ('code', '=ilike', '138' + '%'),
    ])
    accounts_update_to_current_liabilities = env['account.account'].search([
        ('company_id', 'in', companies.ids),
        '|',
            ('code', '=ilike', '335' + '%'),
            ('code', '=ilike', '338' + '%')
    ])
    accounts_update_to_current_assets.write({'user_type_id': account_type_current_assets.id})
    accounts_update_to_current_liabilities.write({'user_type_id': account_type_current_liabilities.id})

def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _update_account_user_type_c200(env)
