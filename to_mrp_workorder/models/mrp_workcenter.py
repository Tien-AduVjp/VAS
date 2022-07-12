from odoo import models


class MrpWorkcenter(models.Model):
    _inherit = 'mrp.workcenter'
    
    def action_work_order(self):
        if self.env.context.get('filter_work_order', False):
            return super(MrpWorkcenter, self).action_work_order()
        else:
            action = self.env.ref('mrp.action_mrp_workorder_workcenter').read()[0]
            return action