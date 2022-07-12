from . import models


def pre_init_hook(cr):
    """
    Pre-populate stored computed/related fields to speedup installation
    """
    cr.execute("""
    SELECT column_name
    FROM information_schema.columns
    WHERE table_name='account_move' and column_name='lines_count';
    """)

    if not cr.fetchone():
        sql = """
        ALTER TABLE account_move ADD COLUMN lines_count integer DEFAULT 0;
        UPDATE account_move AS m SET lines_count = (select count(*) from account_move_line where move_id = m.id);
        """
        cr.execute(sql)
