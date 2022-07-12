from odoo import api, models, fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    pos_session_id = fields.Many2one('pos.session', string='Session', readonly=True,
                                 help="indicates that the sales order was created from this PoS session")

    def _prepare_order_to_create_from_pos_data(self, pos_order_data, order_lines):
        data = {
            'partner_id': pos_order_data['partner_id'],
            'date_order': pos_order_data['creation_date'],
            'pricelist_id': pos_order_data['pricelist_id'],
            'pos_session_id': pos_order_data['session_id'],
            'user_id': pos_order_data['user_id'],
            'state': 'draft',
            'fiscal_position_id': pos_order_data['fiscal_position_id'],
            'order_line': [(0, 0, line) for line in order_lines]
            }
        
        # convert to datetime
        string_date = str(data['date_order'])[0:10]
        string_time = str(data['date_order'])[11:19]
        data['date_order'] = fields.Datetime.to_datetime(string_date + ' ' + string_time)

        pos_config_id = self.env['pos.config'].browse(pos_order_data['pos_config_id'])
        if pos_config_id and pos_config_id.picking_type_id:
            data['warehouse_id'] = pos_config_id.picking_type_id.warehouse_id.id

        return data

    @api.model
    def create_from_ui(self, pos_order_data):
        """ create a sales order from the point of sale ui.
        """
        order_lines = []
        for line in pos_order_data['lines']:
            product = self.env['product.product'].browse(line[2]['product_id'])
            name = product.name_get()[0][1]
            if product.description_sale:
                name += '\n' + product.description_sale
            tax_ids = line[2]['tax_ids'][0][2]
            order_lines.append({
                    'product_id': line[2]['product_id'],
                    'name': name,
                    'product_uom_qty': line[2]['qty'],
                    'price_unit': line[2]['price_unit'],
                    'tax_id': [(6, 0, tax_ids)]
            })
        new_order = self._prepare_order_to_create_from_pos_data(pos_order_data, order_lines)
        order = self.create(new_order)
        return order.id
