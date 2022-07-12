from odoo import api, models, fields


class PosSession(models.Model):
    _inherit = 'pos.session'
    
    sale_order_ids = fields.One2many('sale.order', 'pos_session_id', string='Sales Orders', readonly=True,
                                 help="The sales orders that have been created from this pos session")
    
    sale_orders_count = fields.Integer(string='Sales Order Count', compute='_compute__sale_orders_count')
    
    @api.depends('sale_order_ids')
    def _compute__sale_orders_count(self):
        for r in self:
            r.sale_orders_count = len(r.sale_order_ids)
            
    def action_view_sales_orders(self):
        action = self.env.ref('sale.action_orders')
        result = action.read()[0]

        # reset context & domain
        result['context'] = {}
        result['domain'] = []
        
        # choose the view_mode accordingly
        if self.sale_orders_count != 1:
            result['domain'] = "[('id', 'in', " + str(self.sale_order_ids.ids) + ")]"
        elif self.sale_orders_count == 1:
            res = self.env.ref('sale.view_order_form', False)
            result['views'] = [(res and res.id or False, 'form')]
            result['res_id'] = self.sale_order_ids.id
        return result

