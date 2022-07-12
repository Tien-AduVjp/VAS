from odoo import api, SUPERUSER_ID

VIETNAM_CONTRIB_CODE = [
    'SOCIAL_INSURANCE',
    'HEALTH_INSURANCE',
    'UNEMPLOYMENT_UNSURANCE',
    'LABOR_UNION'
]


def _update_contribution_types(env):
    types = env['hr.payroll.contribution.type'].search([('code', 'in', VIETNAM_CONTRIB_CODE)])
    types.write({
        'computation_method': 'max_unpaid_days',
        'max_unpaid_days': 14,
    })


def _update_contribution_registers(env):
    registers = env['hr.payroll.contribution.register'].search([('type_id.code', 'in', VIETNAM_CONTRIB_CODE)])
    registers.write({
        'computation_method': 'max_unpaid_days',
        'max_unpaid_days': 14,
    })


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _update_contribution_types(env)
    _update_contribution_registers(env)
