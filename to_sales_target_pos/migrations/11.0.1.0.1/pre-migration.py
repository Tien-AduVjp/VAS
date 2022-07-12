def migrate(cr, version):
    """
    The column name `pos_order_line_id` was wrong. This will changed it to pos_order_id
    """
    sql = ""

    cr.execute("""
    SELECT column_name
    FROM information_schema.columns
    WHERE table_name='invoiced_pos_order_team_target' and column_name='pos_order_id';
    """)
    if not cr.fetchone():
        sql += """
        ALTER TABLE invoiced_pos_order_team_target ADD COLUMN pos_order_id integer;
        UPDATE invoiced_pos_order_team_target SET pos_order_id = pos_order_line_id;
        """

    if sql:
        cr.execute(sql)

