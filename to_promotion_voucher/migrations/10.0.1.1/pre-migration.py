
def migrate(cr, version):
    cr.execute("""
        ALTER TABLE voucher_move_order ADD COLUMN warehouse_id integer DEFAULT NULL;

        UPDATE voucher_move_order SET warehouse_id = subquery.warehouse_id
        FROM (SELECT id, warehouse_id FROM stock_location WHERE NOT warehouse_id IS NULL) AS subquery
        WHERE voucher_move_order.location_id = subquery.id
    """)

