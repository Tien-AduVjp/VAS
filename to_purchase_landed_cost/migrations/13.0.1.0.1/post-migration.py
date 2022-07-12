from odoo import api, SUPERUSER_ID


def _remove_purchase_order_stock_entry_link(env):
    env.cr.execute("""
        DELETE FROM account_move_purchase_order_rel WHERE account_move_id IN (
            SELECT DISTINCT ON (account_move_id) account_move_id
            FROM account_move_purchase_order_rel apl
            INNER JOIN account_move m ON m.id = apl.account_move_id AND m.stock_move_id > 0
        )
    """)


def _update_purchase_order_account_move_link(env):
    orders = env['purchase.order'].search([])
    moves = env['account.move'].search([('type', '=', 'in_invoice'), ('invoice_origin', 'in', orders.mapped('name')), ('stock_move_id', '=', False)])
    rel_vals_list = []
    po_vals_list = []
    for order in orders:
        invoice_count = 0
        for move in moves.filtered(lambda m: m.invoice_origin == order.name):
            rel_vals_list.append((order, move))
            invoice_count += 1
        if order.invoice_count != invoice_count:
            po_vals_list.append((invoice_count, order.id))
    if rel_vals_list and po_vals_list:
        query = """
        INSERT INTO account_move_purchase_order_rel (purchase_order_id, account_move_id) VALUES %s ON CONFLICT (purchase_order_id, account_move_id) DO NOTHING;
        """ % (','.join(map(str, [(order.id, move.id) for order, move in rel_vals_list])))
        for q in po_vals_list:
            query += """UPDATE purchase_order SET invoice_count = %s WHERE id=%s;""" % (q)

    # update link between purchase order line and account move line
    for order, move in rel_vals_list:
        for move_line in move.line_ids.filtered(lambda line: not line.purchase_line_id and line.product_id in order.order_line.product_id):
            purchase_line_id = order.order_line.filtered(lambda line: line.product_id == move_line.product_id)
            if purchase_line_id:
                query += """UPDATE account_move_line SET purchase_line_id = %s WHERE id=%s;""" % (purchase_line_id.id, move_line.id)

    env.cr.execute(query)


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _remove_purchase_order_stock_entry_link(env)
    _update_purchase_order_account_move_link(env)
