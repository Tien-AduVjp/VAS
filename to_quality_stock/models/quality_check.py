from odoo import api, fields, models


class QualityCheck(models.Model):
    _inherit = "quality.check"

    picking_id = fields.Many2one('stock.picking', 'Picking', tracking=True, index=True)
    lot_id = fields.Many2one('stock.production.lot', 'Lot', domain="[('product_id', '=', product_id)]", tracking=True)
    picking_type_id = fields.Many2one('stock.picking.type', string='Picking Type', related='picking_id.picking_type_id', store=True, readonly=True, index=True)
    origin = fields.Char(string='Origin', related='picking_id.origin', store=True, index=True, readonly=True)
    procurement_group_id = fields.Many2one('procurement.group', string='Procurement Group', related='picking_id.group_id', store=True, readonly=True, index=True)

    def _redirect_after_pass_fail(self):
        check = self.picking_id.check_ids.filtered(lambda x: x.quality_state == 'none')[:1]
        if check:
            action = self.env['ir.actions.act_window']._for_xml_id('to_quality.quality_check_action_small')
            action['res_id'] = check.id
            return action
        return super(QualityCheck, self)._redirect_after_pass_fail()

    def _prepare_quality_alert_data(self):
        data = super(QualityCheck, self)._prepare_quality_alert_data()
        data['lot_id'] = self.lot_id.id
        return data

