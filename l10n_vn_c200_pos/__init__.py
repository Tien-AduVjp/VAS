from odoo import api, SUPERUSER_ID


def pre_init_hook(cr):
    env = api.Environment(cr, SUPERUSER_ID, {})

    vn_template = env.ref('l10n_vn.vn_template')
    for company in env['res.company'].search([('chart_template_id', '=', vn_template.id)]):
        acc_131 = env['account.account'].search([('company_id', '=', company.id), ('code', '=', '131')], limit=1)
        acc_132 = env['account.account'].search([('company_id', '=', company.id), ('code', '=', '132')], limit=1)

        for pos_payment_method in env['pos.payment.method'].sudo().search([('company_id', '=', company.id), ('receivable_account_id', '=', acc_132.id)]):
            pos_payment_method.write({
                'receivable_account_id': acc_131.id
                })
