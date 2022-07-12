from odoo import api, SUPERUSER_ID


def _remove_62x_to_911_rules(env):
    c200_template = env.ref('l10n_vn.vn_template')
    c200_companies = env['res.company'].search([('chart_template_id', '=', c200_template.id)])
    rules_to_remove = env['balance.carry.forward.rule'].search([('source_account_ids.code', '=like', '62%'),
                                                                ('dest_account_id.code', '=', '911'),
                                                                ('company_id', 'in', c200_companies.ids)])
    rules_to_remove.unlink()


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _remove_62x_to_911_rules(env)

