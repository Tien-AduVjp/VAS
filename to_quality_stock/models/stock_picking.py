from odoo import api, fields, models, _
from odoo.exceptions import UserError


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    quality_alert_count = fields.Integer(compute='_compute_quality_alert_count')
    check_ids = fields.One2many('quality.check', 'picking_id', string='Checks')
    quality_alert_ids = fields.One2many('quality.alert', 'picking_id', string='Alerts')
    quality_check_todo = fields.Boolean(string='Pending checks', compute='_compute_check_todo_fail', store=True)
    quality_check_fail = fields.Boolean(compute='_compute_check_todo_fail', store=True)

    def _compute_quality_alert_count(self):
        for r in self:
            r.quality_alert_count = len(r.quality_alert_ids)

    @api.depends('check_ids', 'check_ids.quality_state')
    def _compute_check_todo_fail(self):
        for r in self:
            todo = fail = False
            if r.check_ids:
                state_vals = r.check_ids.mapped('quality_state')
                if 'fail' in state_vals:
                    fail = True
                if 'none' in state_vals:
                    todo = True
            r.quality_check_fail = fail
            r.quality_check_todo = todo

    def action_view_quality_check(self):
        self.ensure_one()
        quality_checks = self.check_ids.filtered(lambda c: c.quality_state == 'none')
        if quality_checks:
            action = self.env.ref('to_quality.quality_check_action_small').read()[0]
            action['res_id'] = quality_checks[0].id
            action['context'] = self.env.context
            return action
        return False
    
    def _delete_unprocessed_checks(self):
        checks = self.sudo().mapped('check_ids').filtered(lambda c: c.quality_state == 'none')
        checks.unlink()
                
    def action_cancel(self):
        res = super(StockPicking, self).action_cancel()
        self._delete_unprocessed_checks()
        return res
    
    def _create_backorder(self):
        res = super(StockPicking, self)._create_backorder()
        skip_check = self.env.context.get('skip_check', False)
        if skip_check:
            return res
        self._delete_unprocessed_checks()
        res.mapped('move_lines')._create_quality_checks()
        return res

    def action_done(self):
        move_lines = self.mapped('move_line_ids').filtered('qty_done')
        product_to_check = move_lines.mapped('product_id')
        quality_checks = self.mapped('check_ids')
        if quality_checks:
            checks_fail = quality_checks.filtered(lambda c: c.quality_state == 'fail' and c.point_id and c.point_id.no_proceed_if_failed)
            checks_todo = quality_checks.filtered(lambda c: c.quality_state == 'none' and c.product_id in product_to_check)
            if checks_fail:
                quality_points = ', '.join(checks_fail.mapped('point_id.name'))
                raise UserError(_('Quality Points %s don\'t pass the quality checks, so you can\'t do this move\n'
                                  'Please contact the Quality Manager to set the "No Proceed if Failed" of the Quality Point to False '
                                  ', if you still want to move this.') % quality_points)
            if checks_todo:
                quality_checks_todo = ', '.join(checks_todo.mapped('name'))
                raise UserError(_('You must to do the quality checks %s first!') % quality_checks_todo)
        return super(StockPicking, self).action_done()

    def action_view_quality_alert_picking(self):
        self.ensure_one()
        action = self.env.ref('to_quality.quality_alert_action_check').read()[0]
        action['domain'] = [('id', 'in', self.quality_alert_ids.ids)]
        action['context'] = dict(self.env.context,
                                 default_product_id=self.product_id.id,
                                 default_product_tmpl_id=self.product_id.product_tmpl_id.id,
                                 default_picking_id=self.id)
        if self.quality_alert_count == 1:
            action['views'] = [(False, 'form')]
            action['res_id'] = self.quality_alert_ids.id
        else:
            action['views'] = [(False, 'tree'), (False, 'form')]
        return action

    def action_new_quality_alert(self):
        self.ensure_one()
        action = self.env.ref('to_quality.quality_alert_action_check').read()[0]
        action['context'] = dict(self.env.context,
                                 default_product_id=self.product_id.id,
                                 default_product_tmpl_id=self.product_id.product_tmpl_id.id,
                                 default_picking_id=self.id)
        action['views'] = [(False, 'form')]
        return action
