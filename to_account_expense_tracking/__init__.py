from . import models

def pre_init_hook(cr):
    """
    Pre-populate stored computed/related fields to speedup installation
    """
    sql = ""
    # Adding expense_sheet_id
    cr.execute("""
    SELECT column_name
    FROM information_schema.columns
    WHERE table_name='account_move' and column_name='expense_sheet_id';
    """)
    if not cr.fetchone():
        sql += """
        ALTER TABLE account_move ADD COLUMN expense_sheet_id integer DEFAULT NULL;
        UPDATE account_move as a
        SET expense_sheet_id = (SELECT id FROM hr_expense_sheet WHERE a.id = hr_expense_sheet.account_move_id LIMIT 1);
        """
    # Adding account_move_id
    cr.execute("""
    SELECT column_name
    FROM information_schema.columns
    WHERE table_name='hr_expense' and column_name='account_move_id';
    """)
    if not cr.fetchone():
        sql += """
        ALTER TABLE hr_expense ADD COLUMN account_move_id integer DEFAULT NULL;
        UPDATE hr_expense as h
        SET account_move_id = (SELECT account_move_id FROM hr_expense_sheet as hs WHERE h.sheet_id = hs.id LIMIT 1);
        """

    if sql:
        cr.execute(sql)
