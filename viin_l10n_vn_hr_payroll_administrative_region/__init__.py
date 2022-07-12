from . import models
from odoo import api, SUPERUSER_ID
from odoo import fields


def _update_max_contribution_employee_amount(env):
    """
    reference link: http://ketoanthienung.vn/doan-phi-cong-doan-va-kinh-phi-cong-doan.htm
    """
    types = env['hr.payroll.contribution.type'].search([
        ('company_id.partner_id.country_id', '=', env.ref('base.vn').id),
        ('code', '=', 'LABOR_UNION')
        ])

    contributer_registers = env['hr.payroll.contribution.register'].search([('type_id', 'in', types.ids)])
    contributer_registers.write({
        'max_contribution_employee': 149000
    })

    domain = ['|',
        ('date_to', '>', fields.Date.to_date('2021-1-1')),
        ('date_to', '=', False)]
    register_histories = contributer_registers.payroll_contribution_history_ids.filtered_domain(domain)
    register_histories.write({
        'max_contribution_employee': 149000
    })

def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    vietnam = env.ref('base.vn')
    companies = env['res.company'].search([('partner_id.country_id', '=', vietnam.id)])
    env['administrative.region']._l10n_vn_set_minimum_wage()
    companies._l10n_vn_generate_admin_region_payroll_contrib()
    _update_max_contribution_employee_amount(env)
