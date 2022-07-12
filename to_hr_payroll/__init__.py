from . import models
from . import report
from . import wizard

from odoo import api, SUPERUSER_ID, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.sql import create_column, column_exists


####### PRE_INIT_HOOK #######
def _ensure_valid_hr_contracts(env):
        contracts_of_no_job = env['hr.contract'].sudo().search([('job_id', '=', False)])
        if contracts_of_no_job:
            this_module = env['ir.module.module'].search([('name', '=', 'to_hr_payroll')], limit=1)
            raise ValidationError(_("The following contracts have no job position specified. Please specify job position"
                                    " for all the HR Contract before installing the module %s!\n%s")
                                    % (this_module.shortdesc, ", ".join(contracts_of_no_job.mapped('name'))))


def _ensure_no_hr_payroll_installed(env):
    """
    This method ensures the Odoo EE's hr_payroll module is not installed before installing this to_hr_payroll
    """
    hr_payroll_module = env['ir.module.module'].search([('name', '=', 'hr_payroll'), ('state', '=', 'installed')], limit=1)
    if hr_payroll_module:
        to_hr_payroll_module = env['ir.module.module'].search([('name', '=', 'to_hr_payroll')], limit=1)
        raise UserError(_("You must uninstall the module %s (%s) before you could install the module %s (%s).")
                        % (hr_payroll_module.shortdesc, hr_payroll_module.name, to_hr_payroll_module.shortdesc, to_hr_payroll_module.name))


def _backup_children_column(cr):
    """ Save old values of `children` column to another temp column
    """
    if not column_exists(cr, 'hr_employee', 'temp_children'):
        create_column(cr, 'hr_employee', 'temp_children', 'integer')
    cr.execute("UPDATE hr_employee SET temp_children = children;")


####### POST_INIT_HOOK #######
def _generate_salary_structures(env):
    companies = env['res.company'].search([])
    if companies:
        companies._generate_salary_structures()


def _regenerate_timeoff_code(env):
    env['hr.leave.type'].with_context(active_test=False).search([])._compute_code()


def _generate_salary_slip_sequences(env):
    companies = env['res.company'].search([])
    if companies:
        companies._generate_salary_slip_sequences()


def _restore_children_column(cr):
    """ Restore `children` values from `temp_children`, then drop the temp column
    """
    cr.execute("UPDATE hr_employee SET children = temp_children, total_dependant = temp_children;")
    cr.execute("ALTER TABLE hr_employee DROP COLUMN temp_children;")


def _set_default_companies_cycle(env):
    cycle = env.ref('to_hr_payroll.hr_salary_cycle_default')
    env['res.company'].search([]).write({
        'salary_cycle_id': cycle.id
        })


def _compute_contract_personal_tax_rule(env):
    contracts = env['hr.contract'].search([('personal_tax_rule_id', '=', False)])
    if contracts:
        contracts._get_tax_rule()


####### INIT HOOKS #######
def pre_init_hook(cr):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _ensure_no_hr_payroll_installed(env)
    _ensure_valid_hr_contracts(env)
    _backup_children_column(cr)


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _generate_salary_structures(env)
    _regenerate_timeoff_code(env)
    _generate_salary_slip_sequences(env)
    _restore_children_column(cr)
    _set_default_companies_cycle(env)
    _compute_contract_personal_tax_rule(env)
