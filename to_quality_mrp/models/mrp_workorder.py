from odoo import api, fields, models, _
from odoo.exceptions import UserError


class MrpProductionWorkcenterLine(models.Model):
    _name = 'mrp.workorder'
    _inherit = ['mrp.workorder', 'abstract.quality.mrp']

    check_todo = fields.Boolean(compute='_compute_check_todo')
    alert_count = fields.Integer(compute="_compute_alert_count")
    check_ids = fields.One2many('quality.check', 'workorder_id')

    @api.depends('check_ids.quality_state')
    def _compute_check_todo(self):
        super(MrpProductionWorkcenterLine, self)._compute_check_todo('workorder_id')

    def _compute_alert_count(self):
        super(MrpProductionWorkcenterLine, self)._compute_alert_count('operation_id')

    def action_view_quality_alerts_wo(self):
        return super(MrpProductionWorkcenterLine, self).action_view_quality_alerts_mo('operation_id')

    def action_view_quality_alerts(self):
        
        context = {'default_product_id': self.product_id.product_tmpl_id.id,
                   'default_product_tmpl_id': self.product_id.product_tmpl_id.id,
                   'default_operation_id': self.id,
                   'eid': 'to_quality.quality_alert_action_team'}
        return super(MrpProductionWorkcenterLine, self.with_context(context)).action_view_quality_alerts()

    def _prepare_quality_check_vals(self, check_point, production_order):
        self.ensure_one()
        return {
            'workorder_id': self.id,
            'point_id': check_point.id,
            'team_id': check_point.team_id.id,
            'product_id': production_order.product_id.id,
            }

    def _create_checks(self):
        quality_points = self.env['quality.point'].search([
            ('workcenter_id', 'in', self.mapped('workcenter_id').ids),
            ('picking_type_id', 'in', self.mapped('production_id.picking_type_id').ids),
            '|', ('product_id', 'in', self.mapped('production_id.product_id').ids),
            '&', ('product_id', '=', False),
            ('product_tmpl_id', 'in', self.mapped('production_id.product_id.product_tmpl_id').ids)])

        quality_check_vals_list = []
        for r in self:
            production = r.production_id
            points = quality_points.filtered(lambda p: \
                                             p.workcenter_id.id == r.workcenter_id.id and
                                              p.picking_type_id.id == production.picking_type_id.id and
                                               (p.product_id.id == production.product_id.id or
                                                 (p.product_id == False and p.product_tmpl_id.id == production.product_id.product_tmpl_id.id)
                                                 )
                                               )
            for point in points:
                if point.check_execute_now():
                    quality_check_vals_list.append(r._prepare_quality_check_vals(point, production))
        if quality_check_vals_list:
            return self.env['quality.check'].create(quality_check_vals_list)
        else:
            return self.env['quality.check']

    def record_production(self):
        self.ensure_one()
        list_quality_state = []
        for x in self.check_ids:
            list_quality_state.append(x.quality_state == 'none')
        if any(list_quality_state):
            raise UserError(_('You still need to do the quality checks!'))
        super(MrpProductionWorkcenterLine, self).record_production()
        if self.check_ids:
            # Check if you can attribute the lot to the checks
            if (self.production_id.product_id.tracking != 'none') and self.finished_lot_id:
                checks_to_assign = self.check_ids.filtered(lambda x: not x.lot_id)
                if checks_to_assign:
                    checks_to_assign.write({'lot_id': self.finished_lot_id.id})
            if self.qty_producing > 0:
                self._create_checks()

    def check_quality(self):
        context = dict(self.env.context, active_model='mrp.workorder')
        return super(MrpProductionWorkcenterLine, self.with_context(context)).check_quality()

