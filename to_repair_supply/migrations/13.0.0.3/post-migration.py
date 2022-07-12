# -*- coding: utf-8 -*-
from odoo import api, SUPERUSER_ID


def _update_repair_line_supply_stock_move_ids(env):
    # Update value for the new supply_stock_move_ids field on repair.line
    lines = env['repair.line'].search([('supply_stock_move_id', '!=', False)])
    for line in lines:
        line.write({
            'supply_stock_move_ids': [(4, line.supply_stock_move_id.id)]
            })


def _assign_proc_group_for_undone_repair_orders(env):
    # Assign procurement groups for confirmed and undone repair orders
    for order in env['repair.order'].search([('state' ,'not in', ['draft','cancel','done','delivered'])]):
        order._generate_procurement_group()
        part_moves = order.move_ids - order.supply_stock_move_id - order.reserved_completion_stock_move_id
        part_moves.write({'group_id': order.group_id.id})


def _do_reserve_for_confirmed_repair_orders(env):
    # Generate reserving stock moves for confirmed repair orders but not started yet
    for order in env['repair.order'].search([('state' ,'=', 'confirmed')]):
        order.operations.filtered(
            lambda op: op.type == 'add' and \
                   op.product_id.type != 'service' and \
                   not op.reserved_completion_stock_move_id
        )._generate_reserved_completion_moves()


def migrate(cr, version):
    env = api.Environment(cr, SUPERUSER_ID, {})
    _update_repair_line_supply_stock_move_ids(env)
    _assign_proc_group_for_undone_repair_orders(env)
    _do_reserve_for_confirmed_repair_orders(env)
