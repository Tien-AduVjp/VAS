from . import models
from . import wizards


def _adding_new_trip_fields(cr):
    sql = ""

    # Adding trip_id
    cr.execute("""
    SELECT column_name
    FROM information_schema.columns
    WHERE table_name='stock_move' and column_name='trip_id';
    """)
    if not cr.fetchone():
        sql += """
        ALTER TABLE stock_move ADD COLUMN trip_id integer;
        """

    # adding vehicle_id
    cr.execute("""
    SELECT column_name
    FROM information_schema.columns
    WHERE table_name='stock_move' and column_name='vehicle_id';
    """)
    if not cr.fetchone():
        sql += """
        ALTER TABLE stock_move ADD COLUMN vehicle_id integer;
        """

    # adding driver_id
    cr.execute("""
    SELECT column_name
    FROM information_schema.columns
    WHERE table_name='stock_move' and column_name='driver_id';
    """)
    if not cr.fetchone():
        sql += """
        ALTER TABLE stock_move ADD COLUMN driver_id integer;
        """

    if sql:
        cr.execute(sql)


def pre_init_hook(cr):
    _adding_new_trip_fields(cr)
