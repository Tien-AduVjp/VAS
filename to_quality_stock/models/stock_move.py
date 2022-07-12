from collections import defaultdict
from odoo import models


class StockMove(models.Model):
    _inherit = 'stock.move'

    def _prepare_quality_check_values(self, picking, point, product_id):
        return {
            'company_id': picking.company_id.id,
            'point_id': point.id,
            'picking_id': picking.id,
            'team_id': point.team_id.id,
            'product_id': product_id,
        }

    def _create_quality_checks(self):
        quality_points_list = set([])
        vals_list = []
        pick_moves = defaultdict(lambda: self.env['stock.move'])
        for r in self:
            pick_moves[r.picking_id] |= r
        all_quality_points = self.env['quality.point']
        for picking, moves in pick_moves.items():
            domain_point = [('picking_type_id', '=', picking.picking_type_id.id),
                            '|', ('product_id', 'in', moves.mapped('product_id').ids),
                            '&', ('product_id', '=', False), ('product_tmpl_id', 'in', moves.mapped('product_id').mapped('product_tmpl_id').ids)]
            for check in picking.sudo().check_ids:
                key_point = (check.picking_id.id, check.point_id.id, check.team_id.id, check.product_id.id)
                quality_points_list.add(key_point)
            quality_points = all_quality_points.sudo().search(domain_point)
            for point in quality_points:
                if point.check_execute_now():
                    if point.product_id:
                        key_point = (picking.id, point.id, point.team_id.id, point.product_id.id)
                        if key_point not in quality_points_list:
                            vals = self._prepare_quality_check_values(picking, point, point.product_id.id)
                            vals_list.append(vals)
                            quality_points_list.add(key_point)
                    else:
                        products = picking.move_lines.filtered(lambda m: m.product_id.product_tmpl_id == point.product_tmpl_id).mapped('product_id')
                        for product in products:
                            key_point = (picking.id, point.id, point.team_id.id, product.id)
                            if key_point not in quality_points_list:
                                vals = self._prepare_quality_check_values(picking, point, product.id)
                                vals_list.append(vals)
                                quality_points_list.add(key_point)
        if vals_list:
            self.env['quality.check'].create(vals_list)

    def _action_confirm(self, merge=True, merge_into=False):
        stock_moves = super(StockMove, self)._action_confirm(merge=merge, merge_into=merge_into)
        if not self.env.context.get('skip_check', False):
            stock_moves._create_quality_checks()
        return stock_moves
