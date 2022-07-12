from lxml import etree

from odoo import fields, models, api


class MaintenanceRequest(models.Model):
    _inherit = 'maintenance.request'

    production_id = fields.Many2one('mrp.production', string='Manufacturing Order')
    workorder_id = fields.Many2one('mrp.workorder', string='Work Order')

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(MaintenanceRequest, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        if view_type == 'form' and self.env.user.has_group('mrp.group_mrp_user'):
            maintenance_request_form_arch = etree.XML(res['arch'])
            for doc in maintenance_request_form_arch.xpath("//field[@name='equipment_id']"):
                domain = doc.get('domain', False)
                if domain:
                    domain = "['|', ('workcenter_id', '=', False), ('workcenter_id.order_ids', 'in', workorder_id)]" + domain[1:]
                else:
                    domain = "['|', ('workcenter_id', '=', False), ('workcenter_id.order_ids', 'in', workorder_id)]"
                doc.set('domain', domain)
            res['arch'] = etree.tostring(maintenance_request_form_arch)
        return res
