from . import models
from odoo import api, SUPERUSER_ID

def _update_property_vat_ctp_account_id(env):
    vn_coa_templates = env['account.chart.template']._get_installed_vietnam_coa_templates()
    companies = env['res.company'].with_context(active_test=False).search([
        ('chart_template_id', 'in', vn_coa_templates.ids)
    ])
    if companies:
        accounts_1331 = env['account.account'].search([
            ('company_id', 'in', companies.ids),
            ('code', 'like', '1331%'),
        ])
        for company in companies:
            account_1331 = accounts_1331.filtered(lambda a: a.company_id.id == company.id)[:1]
            company.write({'property_vat_ctp_account_id':account_1331.id})

def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _update_property_vat_ctp_account_id(env)
    env['res.company']._update_vat_counterpart_account_for_localization()
