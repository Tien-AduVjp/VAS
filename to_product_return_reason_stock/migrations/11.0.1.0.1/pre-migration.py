def migrate(cr, version):
    cr.execute("""
    CREATE TABLE IF NOT EXISTS stock_picking_return_reason_rel (
        picking_id integer,
        return_reason_id integer
    );
    """)

    cr.execute("""
    SELECT picking_id, return_reason_id from stock_move
    WHERE return_reason_id IS NOT NULL;
    """)

    res = cr.dictfetchall()
    if res:
        sql = """
        INSERT INTO stock_picking_return_reason_rel ("picking_id", return_reason_id)
        VALUES
        """
        r_count = len(res)
        for idx, row in enumerate(res):
            if idx == r_count - 1:
                sql += "(%s, %s)" % (row['picking_id'], row['return_reason_id'])
            else:
                sql += "(%s, %s)," % (row['picking_id'], row['return_reason_id'])
        cr.execute(sql)

