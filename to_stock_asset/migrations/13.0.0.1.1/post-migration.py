from odoo import api, SUPERUSER_ID


def _remove_duplicated_stock_entries(env):
    stock_moves = env['stock.move'].search([('location_dest_id.usage', '=', 'asset_allocation')])\
                             .filtered(lambda m: len(m.account_move_ids) >= 2)

    account_moves_to_unlink = env['account.move']
    for move in stock_moves:
        account_moves_to_unlink |= move.account_move_ids[1:]
    if account_moves_to_unlink:
        account_moves_to_unlink.button_cancel()
        account_moves_to_unlink.with_context(force_delete=True).unlink()


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})

    _remove_duplicated_stock_entries(env)
