from odoo import models, fields, api


class Respartner(models.Model):
    _inherit = 'res.partner'

    lot_ids = fields.One2many('stock.production.lot', 'customer_id', string='Lot/Seri', groups="stock.group_stock_user")
    lot_count = fields.Integer(string='Lot Count', compute='_compute_lot_count', groups="stock.group_stock_user")

    @api.depends('lot_ids')
    def _compute_lot_count(self):
        prod_lot_data = self.env['stock.production.lot'].sudo().read_group([('customer_id', 'in', self.ids)], ['customer_id'], ['customer_id'])
        mapped_data = dict([(dict_data['customer_id'][0], dict_data['customer_id_count']) for dict_data in prod_lot_data])
        for r in self:
            r.lot_count = mapped_data.get(r.id, 0)

    def action_view_stock_production_lot(self):
        lot_ids = self.mapped('lot_ids')
        res = self.env["ir.actions.act_window"]._for_xml_id('stock.action_production_lot_form')
        res['domain'] = "[('id', 'in', %s)]" % str(lot_ids.ids)
        return res
