from . import models


def pre_init_hook(cr):
    """
    Pre-populate stored computed/related fields to speedup installation
    """
    sql = ""
 
    cr.execute("""
    SELECT column_name
    FROM information_schema.columns
    WHERE table_name='purchase_order' and column_name='count_receipt';
    """)
    if not cr.fetchone():
        sql += """
        ALTER TABLE purchase_order ADD COLUMN count_receipt integer DEFAULT NULL;
        UPDATE purchase_order as po1
        SET count_receipt = 
        (SELECT COUNT(*) as count FROM account_move_purchase_order_rel as am_po 
        INNER JOIN purchase_order as po2 ON am_po.purchase_order_id = po2.id
        INNER JOIN account_move as am ON am_po.account_move_id = am.id
        WHERE am.type = 'in_receipt' AND am.state != 'cancel' AND po1.id = am_po.purchase_order_id);
        """
 
    cr.execute("""
    SELECT column_name
    FROM information_schema.columns
    WHERE table_name='purchase_order' and column_name='count_invoice';
    """)
    if not cr.fetchone():
        sql += """
        ALTER TABLE purchase_order ADD COLUMN count_invoice integer DEFAULT NULL;
        UPDATE purchase_order as po1
        SET count_invoice = 
        (SELECT COUNT(*) as count FROM account_move_purchase_order_rel as am_po 
        INNER JOIN purchase_order as po2 ON am_po.purchase_order_id = po2.id
        INNER JOIN account_move as am ON am_po.account_move_id = am.id
        WHERE am.type != 'in_receipt' AND am.state != 'cancel' AND po1.id = am_po.purchase_order_id);
        """
 
    if sql:
        cr.execute(sql)
