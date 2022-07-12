from odoo import api, models


class MrpCostStructure(models.AbstractModel):
    _name = 'report.to_mrp_account.mrp_cost_structure'
    _description = 'MRP Cost Structure Report'

    def get_report_lines(self, productions):
        ProductProduct = self.env['product.product']
        StockMove = self.env['stock.move']
        Uom = self.env['uom.uom']
        lines = []
        for product in productions.mapped('product_id'):
            manufacturing_orders = productions.filtered(lambda production: production.product_id == product)
            total_cost = 0.0

            # get total cost of raw material production
            raw_materials = []
            query_str = """
            WITH svl AS (
                SELECT product_id, value, stock_move_id
                FROM stock_valuation_layer
            )
            SELECT sm.product_id, sm.bom_line_id, SUM(product_qty), ABS(SUM(svl.value))
            FROM stock_move AS sm
            JOIN svl ON svl.stock_move_id = sm.id
            WHERE raw_material_production_id in %s AND state != 'cancel' AND sm.scrapped = false
            GROUP BY sm.bom_line_id, sm.product_id
            """
            self._cr.execute(query_str, (tuple(manufacturing_orders.ids),))
            for product_id, bom_line_id, qty, cost in self._cr.fetchall():
                raw_materials.append({
                    'qty': qty,
                    'cost': cost or 0.0,
                    'product_id': ProductProduct.browse(product_id),
                    'bom_line_id': bom_line_id
                })
                total_cost += cost or 0.0

            # get total cost of scrapped materials
            scraps = StockMove.search([('production_id', 'in', manufacturing_orders.ids),
                                       ('scrapped', '=', True),
                                       ('state', '=', 'done')])
            uom = manufacturing_orders and manufacturing_orders[0].product_uom_id or Uom
            mo_qty = 0
            if any(order.product_uom_id.id != uom.id for order in manufacturing_orders):
                uom = product.uom_id
                for order in manufacturing_orders:
                    qty = sum(order.move_finished_ids.filtered(lambda move: move.state != 'cancel' and move.product_id == product).mapped('product_qty'))
                    if order.product_uom_id.id == uom.id:
                        mo_qty += qty
                    else:
                        mo_qty += order.product_uom_id._compute_quantity(qty, uom)
            else:
                for order in manufacturing_orders:
                    mo_qty += sum(order.move_finished_ids.filtered(lambda move: move.state != 'cancel' and move.product_id == product).mapped('product_qty'))

            for order in manufacturing_orders:
                by_products = order.move_finished_ids.filtered(lambda move: move.state != 'cancel' and move.product_id != product)

            # get total cost of operations
            operations = []
            workorders = self.env['mrp.workorder'].search([('production_id', 'in', manufacturing_orders.ids)])
            if workorders:
                query_str = """SELECT wo.operation_id, rw.name, p.name, sum(wp.duration), wc.costs_hour
                                FROM mrp_workcenter_productivity AS wp
                                LEFT JOIN mrp_workcenter AS wc ON (wc.id = wp.workcenter_id)
                                LEFT JOIN mrp_workorder AS wo ON (wo.id = wp.workorder_id)
                                LEFT JOIN res_users AS u ON (u.id = wp.user_id)
                                LEFT JOIN res_partner AS p ON (p.id = u.partner_id)
                                LEFT JOIN mrp_routing_workcenter AS rw ON (rw.id = wo.operation_id)
                                WHERE wp.workorder_id IS NOT NULL AND wp.workorder_id IN %s
                                GROUP BY wo.operation_id, rw.name, p.name, wp.user_id, wc.costs_hour
                                ORDER BY rw.name, p.name
                            """
                self._cr.execute(query_str, (tuple(workorders.ids),))
                for operation_id, operation_name, user_name, duration, costs_hour in self._cr.fetchall():
                    operations.append([user_name, operation_id, operation_name, duration / 60.0, costs_hour])

            lines.append({
                'by_products': by_products,
                'product': product,
                'operations': operations,
                'currency': self.env.company.currency_id,
                'mo_qty': mo_qty,
                'mo_uom': uom,
                'total_cost': total_cost,
                'raw_materials': raw_materials,
                'scraps': scraps,
                'mo_count': len(manufacturing_orders),
            })
        return lines

    @api.model
    def _get_report_values(self, docids, data=None):
        productions = self.env['mrp.production'].browse(docids).filtered(lambda p: p.state != 'cancel')
        lines = None
        if not any([p.state != 'done' for p in productions]):
            lines = self.get_report_lines(productions)
        return {'lines': lines}
