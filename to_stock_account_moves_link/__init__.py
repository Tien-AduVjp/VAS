from . import models


def pre_init_hook(cr):
    """
    Pre-populate stored computed/related fields to speedup installation
    """
    sql = ""

    cr.execute("""
    SELECT column_name
    FROM information_schema.columns
    WHERE table_name='account_move' and column_name='stock_picking_id';
    """)
    if not cr.fetchone():
        sql += """
        ALTER TABLE account_move ADD COLUMN stock_picking_id integer DEFAULT NULL;
        UPDATE account_move as am
        SET stock_picking_id = (SELECT picking_id FROM stock_move as sm WHERE am.stock_move_id = sm.id LIMIT 1);
        """

    cr.execute("""
    SELECT column_name
    FROM information_schema.columns
    WHERE table_name='account_move_line' and column_name='stock_picking_id';
    """)
    if not cr.fetchone():
        sql += """
        ALTER TABLE account_move_line ADD COLUMN stock_move_id integer DEFAULT NULL;
        UPDATE account_move_line as aml
        SET stock_move_id = (SELECT stock_move_id FROM account_move as am WHERE aml.move_id = am.id LIMIT 1);
        """

    cr.execute("""
    SELECT column_name
    FROM information_schema.columns
    WHERE table_name='account_move_line' and column_name='stock_picking_id';
    """)
    if not cr.fetchone():
        sql += """
        ALTER TABLE account_move_line ADD COLUMN stock_picking_id integer DEFAULT NULL;
        UPDATE account_move_line as aml
        SET stock_picking_id = (SELECT picking_id FROM stock_move as sm WHERE aml.stock_move_id = sm.id LIMIT 1);
        """

    if sql:
        cr.execute(sql)
