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
        super(MrpProductionWorkcenterLine, self)._compute_alert_count('work_order_id')

    def action_view_quality_alerts_wo(self):
        return super(MrpProductionWorkcenterLine, self).action_view_quality_alerts_mo('work_order_id')

    def action_view_quality_alerts(self):
        check_type_prd = self.env['quality.type'].search([('type', '=', 'product')], limit=1)
        context = {'default_type_id': check_type_prd.id,
                   'default_product_id': self.product_id.product_tmpl_id.id,
                   'default_product_tmpl_id': self.product_id.product_tmpl_id.id,
                   'default_work_order_id': self.id,
                   'default_production_id': self.production_id.id,
                   'eid': 'to_quality.quality_alert_action_team'}
        return super(MrpProductionWorkcenterLine, self.with_context(context)).action_view_quality_alerts()

    def _find_candidate_quality_team(self):
        return self.production_id.check_ids.team_id[:1] or self.env['quality.alert.team'].search([], limit=1)

    def _prepare_quality_check_vals(self, quality_point):
        self.ensure_one()
        return {
            'type_id': quality_point.type_id.id,
            'point_id': quality_point.id,
            'workorder_id': self.id,
            'team_id': quality_point.team_id.id,
            'product_id': quality_point.product_id.id,
            }

    def _create_material_checks(self):
        quality_type_prd = self.env['quality.type'].search([('type', '=', 'product')], limit=1)
        if quality_type_prd:
            for r in self:
                bom_lines = r.production_bom_id.bom_line_ids.filtered(lambda line: line.operation_id == r.operation_id)
                quality_point = r.env['quality.point'].search([
                                    ('type_id', '=', quality_type_prd.id),
                                    ('picking_type_id', 'in', r.production_id.picking_type_id.ids),
                                    '|', ('product_id', 'in', bom_lines.product_id.ids),
                                    '&', ('product_id', '=', False),
                                    ('product_tmpl_id', 'in', bom_lines.product_id.product_tmpl_id.ids)])
                if quality_point:
                    r.check_ids = [(5, 0)] +  [(0, 0, r._prepare_quality_check_vals(point)) for point in quality_point]

    def button_finish(self):
        if self.check_ids.filtered(lambda c: c.quality_state == 'none'):
            raise UserError(_('You still need to do the quality checks!'))
        res = super(MrpProductionWorkcenterLine, self).button_finish()
        for r in self:
            if r.check_ids:
                # Check if you can attribute the lot to the checks
                if (r.product_id.tracking != 'none') and self.finished_lot_id:
                    checks_to_assign = self.check_ids.filtered(lambda x: not x.lot_id)
                    if checks_to_assign:
                        checks_to_assign.write({'lot_id': self.finished_lot_id.id})
        return res

    def button_start(self):
        self.ensure_one()
        if self.check_todo:
            raise UserError(_("Before you start, you must conduct a quality check of the materials."))
        return super(MrpProductionWorkcenterLine, self).button_start()

    def check_quality(self):
        context = dict(self.env.context, active_model='mrp.workorder')
        return super(MrpProductionWorkcenterLine, self.with_context(context)).check_quality()
