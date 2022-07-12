def migrate(cr, version):
    sql = ""
    cr.execute("""
    SELECT column_name
    FROM information_schema.columns
    WHERE table_name='pos_order_line' and column_name='return_reason_id';
    """)
    if not cr.fetchone():
        sql += """
        ALTER TABLE pos_order_line ADD COLUMN return_reason_id integer;
        UPDATE pos_order_line SET return_reason_id = pos_order.return_reason_id
            FROM pos_order
            WHERE pos_order_line.order_id = pos_order.id
        """

    if sql:
        cr.execute(sql)
