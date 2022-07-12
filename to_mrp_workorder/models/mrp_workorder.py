from odoo import models, fields, api


class MrpWorkorder(models.Model):
    _name = 'mrp.workorder'
    _inherit = ['mrp.workorder', 'mail.thread', 'mail.activity.mixin']

    product_uom_category_id = fields.Many2one(related='product_id.uom_id.category_id')
    is_last_wo = fields.Boolean(string='Last Work Order', compute='_compute_is_last_wo', store=True)
    is_allowed_create_backorder = fields.Boolean(string='Allowed Create Backorder', compute='_compute_is_allowed_create_backorder', store=True)

    @api.depends('production_id.workorder_ids', 'production_id.workorder_ids.state')
    def _compute_is_last_wo(self):
        for r in self:
            is_last_wo = False
            running_wo = r.production_id.workorder_ids.filtered(lambda x: x.state not in ['done', 'cancel'])
            if running_wo and len(running_wo) == 1:
                is_last_wo = True
            r.is_last_wo = is_last_wo

    @api.depends('qty_producing', 'qty_production')
    def _compute_is_allowed_create_backorder(self):
        for r in self:
            r.is_allowed_create_backorder = r.product_tracking in ['none', False] and r.qty_producing != r.qty_production

    def action_open_form(self):
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id('mrp.mrp_workorder_mrp_production_form')
        action.update({
            'res_id': self.id,
            'target': 'current'
            })
        return action

    def action_show_tablet_view(self):
        self.ensure_one()
        action = self.env['ir.actions.actions']._for_xml_id('to_mrp_workorder.mrp_workorder_tablet_action')
        action['res_id'] = self.id
        return action

    def action_tablet_back(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'mrp.production',
            'views': [[self.env.ref('mrp.mrp_production_form_view').id, 'form']],
            'res_id': self.production_id.id,
            'target': 'main',
        }

    def action_tablet_done(self):
        self.button_done()
        return self.action_tablet_back()

    def action_tablet_validate(self):
        res = self.production_id.with_context(tablet_interface=True).button_mark_done()
        if res is True:
            return self.action_tablet_back()
        return res

    def action_tablet_record_production(self):
        return self.with_context(qty_producing=self.qty_producing).production_id.action_tablet_record_production()

    def action_tablet_generate_serial(self):
        return self.production_id.action_generate_serial()
