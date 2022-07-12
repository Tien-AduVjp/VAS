from odoo import fields, models


class QualityCheck(models.Model):
    _inherit = "quality.check"
    
    production_id = fields.Many2one('mrp.production', 'Production Order')
    workorder_id = fields.Many2one('mrp.workorder', 'Work Order')
    workcenter_id = fields.Many2one('mrp.workcenter', related='workorder_id.workcenter_id', store=True, readonly=True)

    def _redirect_after_pass_fail(self):
        self.ensure_one()
        if not self.production_id or self.workorder_id:
            if self.workorder_id:
                checks = self.workorder_id.check_ids.filtered(lambda x: x.quality_state == 'none')
            else:
                checks = False
        else:
            checks = self.production_id.check_ids.filtered(lambda x: x.quality_state == 'none')
        if not checks:
            return super(QualityCheck, self)._redirect_after_pass_fail()
        else:
            action = self.env.ref('to_quality.quality_check_action_small').read()[0]
            action['res_id'] = checks.ids[0]
            return action
