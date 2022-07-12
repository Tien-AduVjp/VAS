from odoo import api, fields, models, _
from odoo.exceptions import UserError


class MrpProduction(models.Model):
    _name = 'mrp.production'
    _inherit = ['mrp.production', 'abstract.quality.mrp']

    check_ids = fields.One2many('quality.check', 'production_id', string="Checks")
    check_todo = fields.Boolean(compute='_compute_check_todo')
    alert_count = fields.Integer(compute='_compute_alert_count')

    @api.depends('check_ids.quality_state')
    def _compute_check_todo(self):
        super(MrpProduction, self)._compute_check_todo('production_id')

    def _compute_alert_count(self):
        super(MrpProduction, self)._compute_alert_count('production_id')

    def action_view_quality_alerts(self):
        check_type_prd = self.env['quality.type'].search([('type', '=', 'product')], limit=1)
        context = {'default_type_id': check_type_prd.id,
                   'default_product_tmpl_id': self.product_id.product_tmpl_id.id,
                   'default_product_id': self.product_id.product_tmpl_id.id,
                   'user_id': self.user_id.id,
                   'eid': 'to_quality.quality_alert_action_check'}
        return super(MrpProduction, self.with_context(context)).action_view_quality_alerts()

    def action_view_quality_alerts_mo(self):
        return super(MrpProduction, self).action_view_quality_alerts_mo('production_id')

    def _prepare_quality_check_vals(self, check_point):
        self.ensure_one()
        return {
            'type_id': check_point.type_id.id,
            'workorder_id': False,
            'production_id': self.id,
            'point_id': check_point.id,
            'team_id': check_point.team_id.id,
            'product_id': self.product_id.id,
            }

    def action_confirm(self):
        res = super(MrpProduction, self).action_confirm()
        quality_points = self.env['quality.point'].search([
            ('picking_type_id', 'in', self.picking_type_id.ids),
            '|', ('product_id', 'in', self.product_id.ids),
            '&', ('product_id', '=', False),
            ('product_tmpl_id', 'in', self.product_id.product_tmpl_id.ids)])

        quality_check_vals_list = []
        for r in self:
            points = quality_points.filtered(lambda p: \
                                             (p.picking_type_id == r.picking_type_id and
                                              (p.product_id == r.product_id or
                                               (p.product_id == False and p.product_id.product_tmpl_id == r.product_id.product_tmpl_id)
                                               )
                                              )
                                             )
            for point in points:
                if point.check_execute_now():
                    quality_check_vals_list.append(r._prepare_quality_check_vals(point))

        if quality_check_vals_list:
            self.env['quality.check'].create(quality_check_vals_list)
        self.workorder_ids._create_material_checks()
        return res

    def button_mark_done(self):
        for r in self:
            list_quality_state = []
            for x in r.check_ids:
                list_quality_state.append(x.quality_state == 'none')
            if any(list_quality_state):
                raise UserError(_('Please do quality checks!'))
        return super(MrpProduction, self).button_mark_done()
