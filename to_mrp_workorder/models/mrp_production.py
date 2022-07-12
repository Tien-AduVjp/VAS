from odoo import models


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    def button_mark_done(self):
        action = super(MrpProduction, self).button_mark_done()
        if self.env.context.get('tablet_interface'):
            if action is True:
                return action
            backorder = self.browse(action['res_id'])
            workorders = backorder.workorder_ids.filtered(lambda r: r.state not in ['done', 'cancel'])
            if workorders:
                action = self.env['ir.actions.actions']._for_xml_id('to_mrp_workorder.mrp_workorder_tablet_action')
                action['res_id'] = workorders[0].id
        return action

    def action_tablet_record_production(self):
        self._generate_backorder_productions(close_mo=False)
        done_move_finished_ids = self.move_finished_ids.filtered(lambda m: m.state == 'done')
        done_move_finished_ids._trigger_assign()
        self.write({'product_qty': self.env.context.get('qty_producing')})
        return True
