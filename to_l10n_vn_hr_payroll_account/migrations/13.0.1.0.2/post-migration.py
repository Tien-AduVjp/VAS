# -*- coding: utf-8 -*-
from odoo import api, SUPERUSER_ID


def _fix_salary_rule_analytic_option(env):
    vn_coa = env.ref('l10n_vn.vn_template')
    vn_companies = env['res.company'].sudo().search([('chart_template_id', '=', vn_coa.id)])
    if vn_companies:
        affected_rules = env['hr.salary.rule'].sudo().search([
            ('company_id', 'in', vn_companies.ids),
            ('generate_account_move_line', '=', True),
            ('anylytic_option', '=', 'none'),
            ('code', 'in', ('GROSS', 'CSINS', 'CHINS', 'CUEINS', 'CLUF', 'HARMFUL'))])
        if affected_rules:
            affected_rules.sudo().write({
                'anylytic_option': 'debit_account'
                })


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _fix_salary_rule_analytic_option(env)

