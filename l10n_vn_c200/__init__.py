from . import models
from odoo import api, SUPERUSER_ID


def pre_init_hook(cr):
    env = api.Environment(cr, SUPERUSER_ID, {})

    # Fix l10n_vn for account 132. According to Circular 112/2018/TT-BTC, the name of this account is 'Phải thu phí, lệ phí',
    # instead of 'Phải thu của khách hàng (PoS)'
    # see: https://thukyluat.vn/vb/thong-tu-112-2018-tt-btc-sua-doi-thong-tu-174-2015-tt-btc-ve-ke-toan-nghiep-vu-thue-5f90c.html
    env.ref('l10n_vn.chart132').write({'name': 'Phải thu phí, lệ phí'})

    # Fix l10n_vn for pos receivable account
    # It should be 131 instead of 132 which is incorrect
    vn_template = env.ref('l10n_vn.vn_template')
    vn_template.write({
        'default_pos_receivable_account_id': env.ref('l10n_vn.chart131').id
        })
    for company in env['res.company'].search([('chart_template_id', '=', vn_template.id)]):
        acc_131 = env['account.account'].sudo().search([('company_id', '=', company.id), ('code', '=', '131')], limit=1)
        company.write({
            'account_default_pos_receivable_account_id': acc_131.id
            })

        
def _disable_anglo_saxon(env):
    vn_template = env.ref('l10n_vn.vn_template')
    companies_to_fix = env['res.company'].search([
        ('chart_template_id', '=', vn_template.id),
        ('anglo_saxon_accounting', '=', True)
        ])
    if companies_to_fix:
        companies_to_fix.sudo().write({'anglo_saxon_accounting': False})


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})

    _disable_anglo_saxon(env)
    env['account.account'].remove_acc_999999()
    env['res.company'].fix_vietnam_coa()
    env['account.tax.group'].set_tax_group_is_vat_vietnam()

