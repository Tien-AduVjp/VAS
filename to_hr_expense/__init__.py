from odoo import api, SUPERUSER_ID

from . import models
from . import wizards


def _generate_value_for_field(cr):
    """
    Pre-populate stored computed/related fields to speedup installation
    """
    sql = ''
    # Adding expense_sheet_id
    cr.execute('''
    SELECT column_name
    FROM information_schema.columns
    WHERE table_name='account_move' and column_name='expense_sheet_id';
    ''')
    if not cr.fetchone():
        sql += '''
        ALTER TABLE account_move ADD COLUMN expense_sheet_id integer DEFAULT NULL;
        UPDATE account_move as a
        SET expense_sheet_id = (SELECT id FROM hr_expense_sheet WHERE a.id = hr_expense_sheet.account_move_id LIMIT 1);
        '''
    # Adding account_move_id
    cr.execute('''
    SELECT column_name
    FROM information_schema.columns
    WHERE table_name='hr_expense' and column_name='account_move_id';
    ''')
    if not cr.fetchone():
        sql += '''
        ALTER TABLE hr_expense ADD COLUMN account_move_id integer DEFAULT NULL;
        UPDATE hr_expense as h
        SET account_move_id = (SELECT account_move_id FROM hr_expense_sheet as hs WHERE h.sheet_id = hs.id LIMIT 1);
        '''

    if sql:
        cr.execute(sql)


def _create_expense_journal(env):
    companies = env['res.company']
    companies._generate_expense_account_journals()

def pre_init_hook(cr):
    _generate_value_for_field(cr)


def post_init_hook(cr, registry):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env['hr.expense']._update_to_invoice_status_for_existing_expenses()
    _create_expense_journal(env)
