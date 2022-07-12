from . import models
from . import wizard
from odoo import api, SUPERUSER_ID


def _generate_timesheet_approval_types(env):
    companies = env['res.company'].search([])
    companies._generate_approval_request_type()

def _auto_approve_timesheet(cr):
    cr.execute(
        """
            WITH subquery AS (
                    SELECT line.id FROM account_analytic_line AS line
                    LEFT JOIN hr_employee AS employee  ON employee.id = line.employee_id
                    LEFT JOIN hr_contract AS contract ON contract.employee_id = employee.id
                    WHERE line.employee_id IS NULL or line.project_id IS NULL
                    OR line.holiday_id IS NOT NULL
                    OR (
                        contract.id IS NOT NULL AND contract.state IN ('open', 'close')
                        AND (
                                (contract.date_start <= line.date AND contract.date_end IS NULL)
                                OR (contract.date_start <= line.date AND line.date <= contract.date_end)
                            )
                    )
            )
            UPDATE account_analytic_line
            SET timesheet_state = 'validate'
            FROM subquery
            where account_analytic_line.id = subquery.id
            """
    )

def pre_init_hook(cr):
    cr.execute(
        """
        ALTER TABLE account_analytic_line ADD COLUMN IF NOT EXISTS timesheet_state CHARACTER VARYING;
        UPDATE account_analytic_line SET timesheet_state = 'draft';
        """
    )
    _auto_approve_timesheet(cr)

def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _generate_timesheet_approval_types(env)
