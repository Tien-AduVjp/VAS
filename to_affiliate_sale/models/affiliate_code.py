from odoo import fields, models


class AffiliateCode(models.Model):
    _inherit = 'affiliate.code'

    sale_line_ids = fields.One2many('sale.order.line', 'affcode_id', string='Client Sales Order Lines', readonly=True)
    sale_order_ids = fields.One2many('sale.order', 'affcode_id', string='Client Sales Orders', readonly=True)
    sale_orders_count = fields.Integer(string='Sales Orders Count', compute='_compute_sale_orders_count')

    def _compute_sale_orders_count(self):
        order_data = self.env['sale.order'].read_group([('affcode_id', 'in', self.ids)], ['affcode_id'], ['affcode_id'])
        mapped_data = dict([(dict_data['affcode_id'][0], dict_data['affcode_id_count']) for dict_data in order_data])
        for r in self:
            r.sale_orders_count = mapped_data.get(r.id, 0)

    def action_view_client_sale_orders(self):
        result = self.env['ir.actions.act_window']._for_xml_id('sale.action_orders')

        result['context'] = {'default_affcode_id': self[0].id if len(self) >= 1 else False}

        sale_orders = self.mapped('sale_order_ids')
        so_count = len(sale_orders)
        # choose the view_mode accordingly
        if so_count != 1:
            result['domain'] = "[('affcode_id', 'in', %s)]" % str(self.ids)
        elif so_count == 1:
            res = self.env.ref('sale.view_order_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = sale_orders.id
        return result
