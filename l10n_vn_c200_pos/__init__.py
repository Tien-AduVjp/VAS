from odoo import api, SUPERUSER_ID


def _replace_account_132_to_131(env):
    for company in env['res.company'].search([('chart_template_id', '=', env.ref('l10n_vn.vn_template').id)]):
        accounts = env['account.account'].search([('company_id', '=', company.id), ('code', 'in', ('131', '132'))])
        acc_131 = accounts.filtered(lambda a: a.code == '131')[:1]
        acc_132 = accounts.filtered(lambda a: a.code == '132')[:1]
        for pos_payment_method in env['pos.payment.method'].search([('company_id', '=', company.id), ('receivable_account_id', '=', acc_132.id)]):
            pos_payment_method.write({
                'receivable_account_id': acc_131.id
            })


def pre_init_hook(cr):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _replace_account_132_to_131(env)
