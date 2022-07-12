from odoo import api, models

class Repair(models.Model):
    _inherit = 'repair.order'

    @api.onchange('maintenance_request_id')
    def onchange_maintenance_request_id(self):
        repair_lines = self.env['repair.line']
        repair_fees = self.env['repair.fee']
        partner = self.partner_id
        pricelist = self.pricelist_id
        maintenance_schedules = self.maintenance_request_id.equipment_id.maintenance_schedule_ids.filtered(lambda l: l.product_milestone_id.id == self.maintenance_request_id.maintenance_milestone_id.id)
        for maintenance_schedule in maintenance_schedules:
            if maintenance_schedule.part_replacement:
                if pricelist:
                    price = pricelist.get_product_price(maintenance_schedule.product_id, 1, partner, uom_id=maintenance_schedule.product_id.uom_id.id)
                    args = self.company_id and [('company_id', '=', self.company_id.id)] or []
                    warehouse = self.env['stock.warehouse'].search(args, limit=1)
                    code = maintenance_schedule.product_id.default_code or False
                    if code:
                        repair_line_name = '[%s] %s' % (code, maintenance_schedule.product_id.name )
                    else:
                        repair_line_name =  maintenance_schedule.product_id.name
                    repair_lines += repair_lines.new({
                                        'product_id': maintenance_schedule.product_id.id,
                                        'name': repair_line_name,
                                        'type': 'add',
                                        'product_uom_qty': 1.0,
                                        'product_uom': maintenance_schedule.product_id.uom_id,
                                        'price_unit': price and price or 0.0,
                                        'location_id': warehouse.lot_stock_id.id,
                                        'location_dest_id': self.env['stock.location'].search([('usage', '=', 'production')], limit=1).id
                                    })
            if pricelist:
                price = pricelist.get_product_price(maintenance_schedule.maintenance_action_id.service_id, 1, partner, uom_id=maintenance_schedule.maintenance_action_id.service_id.uom_id.id)
            repair_fees += repair_fees.new({
                                        'product_id': maintenance_schedule.maintenance_action_id.service_id.id,
                                        'name': maintenance_schedule.part,
                                        'product_uom_qty': 1.0,
                                        'product_uom': maintenance_schedule.maintenance_action_id.service_id.uom_id,
                                        'price_unit': price and price or 0.0
                                    })
        self.fees_lines = repair_fees
        self.operations = repair_lines
