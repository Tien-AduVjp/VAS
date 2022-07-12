from odoo import api, models, fields


class MaintenanceRequest(models.Model):
    _inherit = "maintenance.request"

    repair_ids = fields.One2many('repair.order', 'maintenance_request_id', string="Repairs")
    repair_count = fields.Integer(string='Repair Count', compute="_compute_repair_count")


    def _compute_repair_count(self):
        repair_data = self.env['repair.order'].sudo().read_group([('maintenance_request_id', 'in', self.ids)], ['maintenance_request_id'], ['maintenance_request_id'])
        mapped_data = dict([(dict_data['maintenance_request_id'][0], dict_data['maintenance_request_id_count']) for dict_data in repair_data])
        for r in self:
            r.repair_count = mapped_data.get(r.id, 0)

    def action_view_repair_history(self):
        self.ensure_one()
        action = self.env['ir.actions.act_window']._for_xml_id('repair.action_repair_order_tree')
        action['context'] = {'search_default_maintenance_request_id': self.id, 'default_maintenance_request_id': self.id}
        return action

    def repair_request_action(self):
        action = self.env['ir.actions.act_window']._for_xml_id('repair.action_repair_order_tree')
        res = self.env.ref('repair.view_repair_order_form', False)
        action['views'] = [(res and res.id or False, 'form')]
        action['context'] = {
            'default_maintenance_request_id': self.id,
            }
        return action
