

def _convert_m2o_to_m2m(cr):
    cr.execute("""
        CREATE TABLE IF NOT EXISTS replenishment_request_stock_picking_rel (
            request_id integer,
            picking_id integer,
            PRIMARY KEY (request_id, picking_id)
        );
        INSERT INTO replenishment_request_stock_picking_rel (picking_id, request_id)
        SELECT id, replenishment_request_id
            FROM stock_picking
            WHERE replenishment_request_id IS NOT NULL;
    """)


def migrate(cr, version):
    _convert_m2o_to_m2m(cr)
