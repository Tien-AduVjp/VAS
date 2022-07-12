import logging

from odoo import api, SUPERUSER_ID
from odoo.models import PREFETCH_MAX
from odoo.tools.sql import create_column, column_exists

from . import models

_logger = logging.getLogger(__name__)


def splittor(rs):
    """ Splits the self recordset in batches of 1000 (to avoid
    entire-recordset-prefetch-effects) & removes the previous batch
    from the cache after it's been iterated in full
    """
    for idx in range(0, len(rs), PREFETCH_MAX):
        sub = rs[idx:idx + PREFETCH_MAX]
        yield sub
        rs.invalidate_cache(ids=sub.ids)


####### START PRE_INIT_HOOK #######
def _add_columns(env):
    if not column_exists(env.cr, 'hr_leave_type', 'pow_timesheet_required'):
        create_column(env.cr, 'hr_leave_type', 'pow_timesheet_required', 'boolean')
    if not column_exists(env.cr, 'hr_leave', 'pow_timesheet_required'):
        create_column(env.cr, 'hr_leave', 'pow_timesheet_required', 'boolean')
    if not column_exists(env.cr, 'account_analytic_line', 'pow_for_timeoff_id'):
        create_column(env.cr, 'account_analytic_line', 'pow_for_timeoff_id', 'integer')


def _update_wfh_leave_types(env):
    wfh_types = env['hr.leave.type'].search([
        ('unpaid', '=', False),
        ('leave_notif_subtype_id', '=', env.ref('hr_holidays.mt_leave_home_working').id)
        ])
    if wfh_types:
        env.cr.execute("""
        UPDATE hr_leave_type
        SET pow_timesheet_required = True
        WHERE pow_timesheet_required = False
            AND id in %s
        """, (tuple(wfh_types.ids),))

        env.cr.execute("""
        UPDATE hr_leave
        SET pow_timesheet_required = True
        WHERE pow_timesheet_required = False
            AND holiday_status_id in %s
        """, (tuple(wfh_types.ids),))

####### END PRE_INIT_HOOK #######


####### START POST_INIT_HOOK #######
def _generate_pow_timesheet_salary_rules(env):
    companies = env['res.company'].search([])
    companies._generate_pow_timesheet_salary_rules()


def _get_to_rec_number(todo, finished):
    to_rec_number = finished + PREFETCH_MAX
    remain = todo - finished
    return to_rec_number if remain >= to_rec_number else remain

    
def _compute_timesheet_for_pow(env):
    pow_timeoff = env['hr.leave'].search([('state', '=', 'validate'), ('pow_timesheet_required', '=', True)])
    if pow_timeoff:
        pow_timeoff.pow_timesheet_ids.write({'pow_for_timeoff_id': False})
        pow_timesheet_candidates = env['account.analytic.line'].search(
            pow_timeoff._get_pow_timesheet_candidates_domain(),
            order='employee_id, date ASC, id ASC'
            )
        candidates_count = len(pow_timesheet_candidates)
        finished = 0
        for candidates in splittor(pow_timesheet_candidates):
            to_rec_number = finished + PREFETCH_MAX
            to_rec_number = to_rec_number if candidates_count - finished >= to_rec_number else candidates_count - finished
            _logger.info(
                "Start computing PoW-Required Time Off for timesheet %s~%s in total %s timesheet records",
                finished + 1, _get_to_rec_number(candidates_count, finished), candidates_count
                )
            with env.cr.savepoint():
                candidates._compute_pow_for_timeoff_id()
            finished += PREFETCH_MAX


def _compute_hr_working_month_calendar_lines(env):
    hr_working_month_calendar_lines = env['hr.working.month.calendar.line'].search([])
    records_count = len(hr_working_month_calendar_lines)
    finished = 0
    for lines in splittor(hr_working_month_calendar_lines):
        _logger.info(
            "Start computing PoW-Timesheet for working month calendar lines %s~%s in total %s records",
            finished + 1, _get_to_rec_number(records_count, finished), records_count
            )
        with env.cr.savepoint():
            lines._compute_pow_timesheet_ids()
        finished += 1000

####### END POST_INIT_HOOK #######


def pre_init_hook(cr):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _add_columns(env)
    _update_wfh_leave_types(env)


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _generate_pow_timesheet_salary_rules(env)
    _compute_timesheet_for_pow(env)
    _compute_hr_working_month_calendar_lines(env)
